#!/usr/bin/env python3
"""
Pytest test suite for compare-har.py

This test suite provides comprehensive coverage for the HAR file comparison tool,
including unit tests for individual functions and integration tests for the
complete workflow.

Run tests with: pytest test_compare_har.py -v
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open, MagicMock
import pandas as pd
import matplotlib.pyplot as plt

# Import the functions we want to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from compare_har import load_har, extract_timings, compare_har_files


class TestLoadHar:
    """Test cases for the load_har function."""
    
    def test_load_valid_har_file(self):
        """Test loading a valid HAR file."""
        # Create sample HAR data
        sample_har = {
            "log": {
                "version": "1.2",
                "entries": [
                    {
                        "request": {"url": "https://example.com"},
                        "response": {"status": 200},
                        "timings": {"wait": 100, "receive": 50}
                    }
                ]
            }
        }
        
        # Create a temporary file with the sample data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.har', delete=False) as f:
            json.dump(sample_har, f)
            temp_file = f.name
        
        try:
            # Test loading the file
            result = load_har(temp_file)
            assert result == sample_har
            assert "log" in result
            assert "entries" in result["log"]
        finally:
            # Clean up the temporary file
            os.unlink(temp_file)
    
    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_har("nonexistent_file.har")
    
    def test_load_invalid_json(self):
        """Test loading a file with invalid JSON."""
        # Create a temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.har', delete=False) as f:
            f.write("{ invalid json content")
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_har(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_load_empty_file(self):
        """Test loading an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.har', delete=False) as f:
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_har(temp_file)
        finally:
            os.unlink(temp_file)


class TestExtractTimings:
    """Test cases for the extract_timings function."""
    
    def test_extract_complete_timings(self):
        """Test extracting timings when all values are present."""
        entry = {
            "timings": {
                "blocked": 10,
                "dns": 20,
                "connect": 30,
                "send": 5,
                "wait": 100,
                "receive": 25
            }
        }
        
        result = extract_timings(entry)
        
        assert result["blocked"] == 10
        assert result["dns"] == 20
        assert result["connect"] == 30
        assert result["send"] == 5
        assert result["wait"] == 100
        assert result["receive"] == 25
        assert result["total"] == 190  # Sum of all positive values
    
    def test_extract_partial_timings(self):
        """Test extracting timings when some values are missing."""
        entry = {
            "timings": {
                "wait": 100,
                "receive": 50
                # Missing: blocked, dns, connect, send
            }
        }
        
        result = extract_timings(entry)
        
        assert result["blocked"] == 0
        assert result["dns"] == 0
        assert result["connect"] == 0
        assert result["send"] == 0
        assert result["wait"] == 100
        assert result["receive"] == 50
        assert result["total"] == 150
    
    def test_extract_timings_with_negative_values(self):
        """Test extracting timings with negative values (which should be excluded from total)."""
        entry = {
            "timings": {
                "blocked": -1,  # Negative value (indicates unavailable)
                "dns": 20,
                "connect": -1,  # Negative value (indicates unavailable)
                "send": 5,
                "wait": 100,
                "receive": 25
            }
        }
        
        result = extract_timings(entry)
        
        assert result["blocked"] == -1
        assert result["dns"] == 20
        assert result["connect"] == -1
        assert result["send"] == 5
        assert result["wait"] == 100
        assert result["receive"] == 25
        assert result["total"] == 150  # Only positive values: 20 + 5 + 100 + 25
    
    def test_extract_timings_empty(self):
        """Test extracting timings from empty timings object."""
        entry = {"timings": {}}
        
        result = extract_timings(entry)
        
        assert result["blocked"] == 0
        assert result["dns"] == 0
        assert result["connect"] == 0
        assert result["send"] == 0
        assert result["wait"] == 0
        assert result["receive"] == 0
        assert result["total"] == 0
    
    def test_extract_timings_with_float_values(self):
        """Test extracting timings with floating point values."""
        entry = {
            "timings": {
                "blocked": 10.5,
                "dns": 20.25,
                "connect": 30.75,
                "send": 5.1,
                "wait": 100.9,
                "receive": 25.3
            }
        }
        
        result = extract_timings(entry)
        
        assert result["blocked"] == 10.5
        assert result["dns"] == 20.25
        assert result["connect"] == 30.75
        assert result["send"] == 5.1
        assert result["wait"] == 100.9
        assert result["receive"] == 25.3
        assert abs(result["total"] - 192.8) < 0.001  # Account for floating point precision
    
    def test_extract_timings_with_none_values(self):
        """Test extract_timings with None values in timings."""
        entry = {
            "timings": {
                "wait": None,
                "receive": 50,
                "connect": None
            }
        }
        
        result = extract_timings(entry)
        
        # None values should be treated as 0
        assert result["wait"] == 0
        assert result["receive"] == 50
        assert result["connect"] == 0
        assert result["total"] == 50


class TestCompareHarFiles:
    """Test cases for the compare_har_files function."""
    
    def create_sample_har(self, entries_data):
        """Helper method to create a sample HAR structure."""
        return {
            "log": {
                "version": "1.2",
                "entries": entries_data
            }
        }
    
    def create_sample_entry(self, url, status=200, timings=None):
        """Helper method to create a sample HAR entry."""
        if timings is None:
            timings = {"wait": 100, "receive": 50, "connect": 30}
        
        return {
            "request": {"url": url},
            "response": {"status": status},
            "timings": timings
        }
    
    @patch('compare_har.load_har')
    @patch('compare_har.plt.show')
    @patch('compare_har.plt.savefig')
    @patch('pandas.DataFrame.to_csv')
    @patch('builtins.open', new_callable=mock_open)
    def test_compare_basic_functionality(self, mock_file, mock_to_csv, mock_savefig, mock_show, mock_load_har):
        """Test basic comparison functionality with common URLs."""
        # Create sample data
        entry1 = self.create_sample_entry("https://example.com/api", 200, 
                                         {"wait": 100, "receive": 50, "connect": 30})
        entry2 = self.create_sample_entry("https://example.com/api", 200, 
                                         {"wait": 120, "receive": 60, "connect": 35})
        
        har1 = self.create_sample_har([entry1])
        har2 = self.create_sample_har([entry2])
        
        mock_load_har.side_effect = [har1, har2]
        
        # Capture output by redirecting stdout
        with patch('builtins.print') as mock_print:
            compare_har_files("file1.har", "file2.har", top_n=1)
        
        # Verify that load_har was called with correct arguments
        assert mock_load_har.call_count == 2
        mock_load_har.assert_any_call("file1.har")
        mock_load_har.assert_any_call("file2.har")
        
        # Verify that visualization functions were called
        mock_savefig.assert_called_once_with("latency_deltas.png")
        mock_show.assert_called_once()
        
        # Verify CSV export was called
        mock_to_csv.assert_called_once_with('slowest_requests.csv', index=False)
        
        # Verify JSON file was opened for writing
        mock_file.assert_called_with('slowest_requests.json', 'w', encoding='utf-8')
    
    @patch('compare_har.load_har')
    def test_compare_no_common_urls(self, mock_load_har):
        """Test comparison when there are no common URLs."""
        entry1 = self.create_sample_entry("https://example.com/api1")
        entry2 = self.create_sample_entry("https://example.com/api2")
        
        har1 = self.create_sample_har([entry1])
        har2 = self.create_sample_har([entry2])
        
        mock_load_har.side_effect = [har1, har2]
        
        with patch('builtins.print') as mock_print:
            compare_har_files("file1.har", "file2.har")
        
        # Check that the "no common URLs" message was printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("No common URLs found" in call for call in print_calls)
    
    @patch('compare_har.load_har')
    @patch('compare_har.plt.show')
    @patch('compare_har.plt.savefig')
    @patch('pandas.DataFrame.to_csv')
    @patch('builtins.open', new_callable=mock_open)
    def test_compare_with_domain_filter(self, mock_file, mock_to_csv, mock_savefig, mock_show, mock_load_har):
        """Test comparison with domain filtering."""
        entry1 = self.create_sample_entry("https://api.example.com/data")
        entry2 = self.create_sample_entry("https://cdn.example.com/assets")
        entry3 = self.create_sample_entry("https://api.example.com/data")
        entry4 = self.create_sample_entry("https://cdn.example.com/assets")
        
        har1 = self.create_sample_har([entry1, entry2])
        har2 = self.create_sample_har([entry3, entry4])
        
        mock_load_har.side_effect = [har1, har2]
        
        with patch('builtins.print'):
            compare_har_files("file1.har", "file2.har", domain_filter="api.example.com")
        
        # Verify load_har was called
        assert mock_load_har.call_count == 2
    
    @patch('compare_har.load_har')
    @patch('compare_har.plt.show')
    @patch('compare_har.plt.savefig')
    @patch('pandas.DataFrame.to_csv')
    @patch('builtins.open', new_callable=mock_open)
    def test_compare_with_status_filter(self, mock_file, mock_to_csv, mock_savefig, mock_show, mock_load_har):
        """Test comparison with status code filtering."""
        entry1 = self.create_sample_entry("https://example.com/api", 200)
        entry2 = self.create_sample_entry("https://example.com/error", 404)
        entry3 = self.create_sample_entry("https://example.com/api", 200)
        entry4 = self.create_sample_entry("https://example.com/error", 404)
        
        har1 = self.create_sample_har([entry1, entry2])
        har2 = self.create_sample_har([entry3, entry4])
        
        mock_load_har.side_effect = [har1, har2]
        
        with patch('builtins.print'):
            compare_har_files("file1.har", "file2.har", status_filter=200)
        
        # Verify load_har was called
        assert mock_load_har.call_count == 2
    
    @patch('compare_har.load_har')
    def test_timing_calculations(self, mock_load_har):
        """Test that timing calculations are correct."""
        # Create entries with known timing differences
        entry1 = self.create_sample_entry("https://example.com/api", 200, 
                                         {"wait": 100, "receive": 50, "connect": 30, "dns": 10, "blocked": 5, "send": 5})
        entry2 = self.create_sample_entry("https://example.com/api", 200, 
                                         {"wait": 150, "receive": 75, "connect": 45, "dns": 15, "blocked": 10, "send": 10})
        
        har1 = self.create_sample_har([entry1])
        har2 = self.create_sample_har([entry2])
        
        mock_load_har.side_effect = [har1, har2]
        
        # Capture the printed output to verify calculations
        with patch('builtins.print') as mock_print, \
             patch('compare_har.plt.show'), \
             patch('compare_har.plt.savefig'), \
             patch('pandas.DataFrame.to_csv'), \
             patch('builtins.open', mock_open()):
            compare_har_files("file1.har", "file2.har", top_n=1)
        
        # Verify that calculations were performed
        assert mock_load_har.call_count == 2
        
        # Check that timing differences were calculated and printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        timing_output = ''.join(print_calls)
        assert "Δ" in timing_output  # Delta symbol should appear in timing differences


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_end_to_end_with_real_files(self):
        """Test the complete workflow with actual temporary HAR files."""
        # Create sample HAR data
        har1_data = {
            "log": {
                "version": "1.2",
                "entries": [
                    {
                        "request": {"url": "https://example.com/api/users"},
                        "response": {"status": 200},
                        "timings": {"wait": 100, "receive": 50, "connect": 30, "dns": 10, "blocked": 5, "send": 5}
                    },
                    {
                        "request": {"url": "https://example.com/api/posts"},
                        "response": {"status": 200},
                        "timings": {"wait": 80, "receive": 40, "connect": 25, "dns": 8, "blocked": 3, "send": 4}
                    }
                ]
            }
        }
        
        har2_data = {
            "log": {
                "version": "1.2",
                "entries": [
                    {
                        "request": {"url": "https://example.com/api/users"},
                        "response": {"status": 200},
                        "timings": {"wait": 120, "receive": 60, "connect": 35, "dns": 12, "blocked": 7, "send": 6}
                    },
                    {
                        "request": {"url": "https://example.com/api/posts"},
                        "response": {"status": 200},
                        "timings": {"wait": 90, "receive": 45, "connect": 28, "dns": 9, "blocked": 4, "send": 5}
                    }
                ]
            }
        }
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.har', delete=False) as f1:
            json.dump(har1_data, f1)
            file1_path = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.har', delete=False) as f2:
            json.dump(har2_data, f2)
            file2_path = f2.name
        
        try:
            # Run the comparison with mocked output functions
            with patch('builtins.print'), \
                 patch('compare_har.plt.show'), \
                 patch('compare_har.plt.savefig'), \
                 patch('pandas.DataFrame.to_csv'), \
                 patch('json.dump'):  # Mock JSON dump instead of file open
                
                # This should run without errors
                compare_har_files(file1_path, file2_path, top_n=2)
                
        finally:
            # Clean up temporary files
            os.unlink(file1_path)
            os.unlink(file2_path)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @patch('compare_har.load_har')
    def test_empty_har_files(self, mock_load_har):
        """Test comparison with empty HAR files."""
        empty_har = {"log": {"entries": []}}
        mock_load_har.side_effect = [empty_har, empty_har]
        
        with patch('builtins.print') as mock_print:
            compare_har_files("file1.har", "file2.har")
        
        # Should print "no common URLs" message
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("No common URLs found" in call for call in print_calls)
    
    @patch('compare_har.load_har')
    @patch('compare_har.plt.show')
    @patch('compare_har.plt.savefig')
    @patch('pandas.DataFrame.to_csv')
    @patch('builtins.open', new_callable=mock_open)
    def test_single_entry(self, mock_file, mock_to_csv, mock_savefig, mock_show, mock_load_har):
        """Test comparison with single entry in each file."""
        entry1 = {
            "request": {"url": "https://example.com/api"},
            "response": {"status": 200},
            "timings": {"wait": 100, "receive": 50}
        }
        entry2 = {
            "request": {"url": "https://example.com/api"},
            "response": {"status": 200},
            "timings": {"wait": 150, "receive": 75}
        }
        
        har1 = {"log": {"entries": [entry1]}}
        har2 = {"log": {"entries": [entry2]}}
        
        mock_load_har.side_effect = [har1, har2]
        
        with patch('builtins.print'):
            compare_har_files("file1.har", "file2.har", top_n=1)
        
        # Should complete without errors
        assert mock_load_har.call_count == 2
    
    @patch('compare_har.load_har')
    @patch('compare_har.plt.show')
    @patch('compare_har.plt.savefig')
    @patch('pandas.DataFrame.to_csv')
    @patch('builtins.open', new_callable=mock_open)
    def test_multiple_entries_same_url(self, mock_file, mock_to_csv, mock_savefig, mock_show, mock_load_har):
        """Test comparison when multiple entries have the same URL."""
        # This tests the behavior when URLs are duplicated
        entry1a = {
            "request": {"url": "https://example.com/api"},
            "response": {"status": 200},
            "timings": {"wait": 100, "receive": 50}
        }
        entry1b = {
            "request": {"url": "https://example.com/api"},
            "response": {"status": 200},
            "timings": {"wait": 110, "receive": 55}
        }
        entry2 = {
            "request": {"url": "https://example.com/api"},
            "response": {"status": 200},
            "timings": {"wait": 150, "receive": 75}
        }
        
        har1 = {"log": {"entries": [entry1a, entry1b]}}
        har2 = {"log": {"entries": [entry2]}}
        
        mock_load_har.side_effect = [har1, har2]
        
        with patch('builtins.print'):
            # Should handle duplicate URLs (last one wins in dictionary)
            compare_har_files("file1.har", "file2.har", top_n=1)
        
        assert mock_load_har.call_count == 2


class TestParameterValidation:
    """Test parameter validation and edge cases."""
    
    @patch('compare_har.load_har')
    @patch('compare_har.plt.show')
    @patch('compare_har.plt.savefig')
    @patch('pandas.DataFrame.to_csv')
    @patch('builtins.open', new_callable=mock_open)
    def test_top_n_parameter(self, mock_file, mock_to_csv, mock_savefig, mock_show, mock_load_har):
        """Test that top_n parameter works correctly."""
        # Create multiple entries to test top_n functionality
        entries1 = []
        entries2 = []
        
        for i in range(5):
            url = f"https://example.com/api/{i}"
            entries1.append({
                "request": {"url": url},
                "response": {"status": 200},
                "timings": {"wait": 100 + i, "receive": 50}
            })
            entries2.append({
                "request": {"url": url},
                "response": {"status": 200},
                "timings": {"wait": 150 + i * 2, "receive": 75}  # Increasing differences
            })
        
        har1 = {"log": {"entries": entries1}}
        har2 = {"log": {"entries": entries2}}
        
        mock_load_har.side_effect = [har1, har2]
        
        with patch('builtins.print'):
            compare_har_files("file1.har", "file2.har", top_n=3)
        
        assert mock_load_har.call_count == 2


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])