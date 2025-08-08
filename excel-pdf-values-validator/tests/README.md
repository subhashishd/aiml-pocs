# Tests

This directory contains all test files for the Excel-PDF Values Validator application.

## Test Structure

- `test_local.py` - Basic local testing script for quick validation
- `test_pdf_processor.py` - Unit tests for PDF processing functionality  
- `test_excel_processor.py` - Unit tests for Excel processing functionality
- `test_integration.py` - Integration tests for end-to-end workflow
- `run_tests.py` - Test runner script to execute all tests

## Running Tests

### Prerequisites

Install required Python packages:
```bash
pip install PyMuPDF openpyxl pandas sentence-transformers
```

### Run All Tests
```bash
cd tests/
python run_tests.py
```

### Run Individual Test Files
```bash
# Basic local test
python test_local.py

# PDF processing tests
python -m unittest test_pdf_processor.py

# Excel processing tests  
python -m unittest test_excel_processor.py

# Integration tests
python -m unittest test_integration.py
```

### Run Specific Test Methods
```bash
python -m unittest test_integration.TestIntegration.test_end_to_end_workflow
```

## Test Data

Tests use sample files from the `../files/` directory:
- `BunkerDeliveryNote-1.16.3.PDF` - Sample PDF with parameter-value tables
- `output_parameters.xlsx` - Sample Excel file with validation parameters

## Test Coverage

- **PDF Processing**: Table extraction, parameter-value pair identification, text parsing
- **Excel Processing**: Parameter extraction, data validation, format handling
- **Integration**: End-to-end workflow, validation logic, edge cases
- **Edge Cases**: None value handling, string/float conversion, precision handling

## Docker Testing

After running local tests successfully, you can test the Docker deployment:

```bash
# Build and run with docker-compose
cd ..
docker-compose -f docker-compose.dev.yml up --build

# Test the API endpoints
curl http://localhost:8000/health
```

## Troubleshooting

1. **Import Errors**: Ensure you're running from the correct directory and dependencies are installed
2. **File Not Found**: Verify sample files exist in `../files/` directory  
3. **Docker Issues**: Ensure Docker Desktop is running before container tests
4. **Model Download**: First run may be slow due to model downloads
