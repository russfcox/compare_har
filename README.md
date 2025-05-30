# HAR File Comparison Tool

A Python tool for analyzing and comparing HTTP Archive (HAR) files to identify performance differences between different environments or test runs.

## Overview

This tool extracts timing data from HAR files, identifies slow requests, and generates visualizations to help understand performance characteristics. HAR files contain detailed timing information about web requests including DNS lookup time, connection establishment time, SSL handshake time, request/response times, and content download time.

## Features

- Compare timing data between two HAR files
- Filter requests by domain or HTTP status code
- Calculate timing differences for each request phase
- Identify slowest requests with biggest performance regressions
- Export results to CSV and JSON formats
- Generate horizontal bar chart visualizations
- Comprehensive error handling and validation

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Dependencies

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pandas matplotlib
```

Note: `argparse` and `json` are included in Python's standard library.

## Usage

### Basic Usage

```bash
python compare-har.py file1.har file2.har
```

### Advanced Usage

```bash
# Filter by domain
python compare-har.py baseline.har test.har --filter-domain api.example.com

# Filter by HTTP status code
python compare-har.py baseline.har test.har --filter-status 200

# Analyze top 20 slowest requests
python compare-har.py baseline.har test.har --top-n 20

# Combine filters
python compare-har.py baseline.har test.har --filter-domain api.example.com --filter-status 200 --top-n 15
```

### Command Line Arguments

- `file1`: Path to the first HAR file (baseline)
- `file2`: Path to the second HAR file (comparison)
- `--filter-domain`: Only include requests containing this domain substring
- `--filter-status`: Only include requests with this HTTP status code
- `--top-n`: Number of slowest requests to analyze (default: 10)

### Output Files

The tool generates the following output files:

- `slowest_requests.csv`: CSV file with timing data for the slowest requests
- `slowest_requests.json`: JSON file with detailed timing breakdown
- `latency_deltas.png`: Horizontal bar chart visualization

## Testing

This project includes a comprehensive test suite using pytest to ensure reliability and correctness.

### Test Structure

The test suite is organized into several test classes:

- **TestLoadHar**: Tests for HAR file loading functionality
- **TestExtractTimings**: Tests for timing data extraction
- **TestCompareHarFiles**: Tests for the main comparison logic
- **TestIntegration**: End-to-end integration tests
- **TestEdgeCases**: Edge cases and error conditions
- **TestParameterValidation**: Parameter validation tests

### Setting Up the Test Environment

1. **Install test dependencies:**

```bash
pip install -r requirements-test.txt
```

The test requirements include:
- `pytest>=7.0.0` - Core testing framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `pytest-mock>=3.10.0` - Enhanced mocking capabilities
- `pytest-mpl>=0.16.0` - Matplotlib testing support
- `pytest-html>=3.1.0` - HTML test reports
- `pytest-json-report>=1.5.0` - JSON test reports

### Running Tests

#### Basic Test Execution

```bash
# Run all tests with verbose output
pytest tests/test_compare_har.py -v

# Run tests with short traceback
pytest tests/test_compare_har.py --tb=short

# Run tests with detailed traceback
pytest tests/test_compare_har.py --tb=long

# Or run from the tests directory
cd tests
pytest test_compare_har.py -v
```

#### Using the Test Runner Script

The project includes a convenient test runner script:

```bash
# Run from project root
python tests/run_tests.py

# Or run from tests directory
cd tests
python run_tests.py
```

This script will:
- Check if pytest is installed
- Verify the main module exists
- Run multiple test configurations
- Provide a summary of results

#### Running Specific Test Categories

```bash
# Run only HAR loading tests
pytest tests/test_compare_har.py -k "test_load" -v

# Run only timing extraction tests
pytest tests/test_compare_har.py -k "test_extract" -v

# Run only comparison function tests
pytest tests/test_compare_har.py -k "test_compare" -v

# Run only integration tests
pytest tests/test_compare_har.py -k "integration" -v

# Run only edge case tests
pytest tests/test_compare_har.py -k "edge_case" -v
```

#### Test Coverage

Generate test coverage reports:

```bash
# Run tests with coverage report in terminal
pytest tests/test_compare_har.py --cov=compare_har --cov-report=term

# Generate HTML coverage report
pytest tests/test_compare_har.py --cov=compare_har --cov-report=html

# Generate both terminal and HTML reports
pytest tests/test_compare_har.py --cov=compare_har --cov-report=term --cov-report=html
```

The HTML coverage report will be generated in the `htmlcov/` directory. Open `htmlcov/index.html` in a browser to view detailed coverage information.

#### Advanced Test Options

```bash
# Run tests in parallel (requires pytest-xdist)
pytest test_compare_har.py -n auto

# Generate HTML test report
pytest test_compare_har.py --html=report.html --self-contained-html

# Generate JSON test report
pytest test_compare_har.py --json-report --json-report-file=report.json

# Run tests with specific markers
pytest test_compare_har.py -m "unit" -v
pytest test_compare_har.py -m "integration" -v
```

### Test Configuration

The project includes a `pytest.ini` configuration file with the following settings:

- **Test Discovery**: Automatically finds test files matching `test_*.py` pattern
- **Output Format**: Verbose output with short tracebacks
- **Markers**: Custom markers for categorizing tests
- **Color Output**: Enabled for better readability

### Understanding Test Results

#### Successful Test Run

```
========================= test session starts =========================
collected 25 items

test_compare_har.py::TestLoadHar::test_load_valid_har_file PASSED
test_compare_har.py::TestLoadHar::test_load_nonexistent_file PASSED
test_compare_har.py::TestExtractTimings::test_extract_complete_timings PASSED
...
========================= 25 passed in 2.34s =========================
```

#### Failed Test Run

```
========================= FAILURES =========================
_______ TestLoadHar.test_load_invalid_json _______

    def test_load_invalid_json(self):
>       with pytest.raises(json.JSONDecodeError):
E       Failed: DID NOT RAISE json.JSONDecodeError

test_compare_har.py:89: AssertionError
========================= 1 failed, 24 passed in 2.45s =========================
```

### Troubleshooting Tests

#### Common Issues

1. **Import Errors**
   ```bash
   ModuleNotFoundError: No module named 'compare_har'
   ```
   **Solution**: Ensure `compare_har.py` is in the same directory as the test file.

2. **Missing Dependencies**
   ```bash
   ModuleNotFoundError: No module named 'pytest'
   ```
   **Solution**: Install test dependencies with `pip install -r requirements-test.txt`

3. **File Permission Errors**
   ```bash
   PermissionError: [Errno 13] Permission denied
   ```
   **Solution**: Ensure you have write permissions in the test directory for temporary files.

#### Debugging Failed Tests

1. **Use verbose output**: Add `-v` flag to see detailed test names
2. **Use detailed tracebacks**: Add `--tb=long` for full error details
3. **Run specific tests**: Use `-k "test_name"` to run only failing tests
4. **Add print statements**: Temporarily add debug prints in test code
5. **Use pytest debugger**: Add `--pdb` flag to drop into debugger on failures

### Continuous Integration

For CI/CD pipelines, use these commands:

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements-test.txt

# Run tests with coverage and generate reports
pytest tests/test_compare_har.py --cov=compare_har --cov-report=xml --cov-report=term --junit-xml=test-results.xml

# Check coverage threshold (example: 90%)
pytest tests/test_compare_har.py --cov=compare_har --cov-fail-under=90
```

### Contributing

When contributing to this project:

1. **Write tests** for new functionality
2. **Run the full test suite** before submitting changes
3. **Maintain test coverage** above 90%
4. **Follow naming conventions** for test functions (`test_*`)
5. **Add docstrings** to test functions explaining what they test
6. **Use appropriate assertions** and error checking

### Test File Structure

```
project/
├── compare_har.py          # Main application code
├── tests/                  # Test directory
│   ├── __init__.py         # Test package init
│   ├── test_compare_har.py # Test suite
│   ├── pytest.ini         # Pytest configuration
│   ├── requirements-test.txt # Test dependencies
│   └── run_tests.py        # Test runner script
└── README.md              # This file
```

## Example HAR File Structure

HAR files are JSON format files with the following structure:

```json
{
  "log": {
    "version": "1.2",
    "entries": [
      {
        "request": {
          "url": "https://example.com/api"
        },
        "response": {
          "status": 200
        },
        "timings": {
          "blocked": 10,
          "dns": 20,
          "connect": 30,
          "send": 5,
          "wait": 100,
          "receive": 25
        }
      }
    ]
  }
}
```

## Timing Phases Explained

- **blocked**: Time spent in a queue waiting for a network connection
- **dns**: DNS resolution time
- **connect**: Time to establish TCP connection
- **send**: Time to send HTTP request to server
- **wait**: Time waiting for response from server (server processing time)
- **receive**: Time to download the response from server

## License

This project is open source. Please refer to the license file for details.

## Support

For issues, questions, or contributions, please refer to the project's issue tracker or documentation.