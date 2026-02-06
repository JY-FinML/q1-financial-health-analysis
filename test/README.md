# Test Instructions

## Quick test commands

```bash
# Run all tests
python -m pytest test/

# Run unit tests
python -m pytest test/unit_test/

# Run integration tests
python -m pytest test/integration_test/

# Quiet output
python -m pytest test/ -q

# Verbose output
python -m pytest test/ -v
```

## Test structure

```
test/
├── conftest.py                      # Shared fixtures (test data and helpers)
├── unit_test/                       # Unit tests
│   ├── test_company_forecast/       # Unit tests for the company_forecast module
│   └── test_data/                   # Unit tests for the data module
└── integration_test/                # Integration tests
    ├── test_company_forecast/       # Integration tests for the company_forecast module
    └── test_data/                   # Integration tests for the data module
```

## Folder naming convention

Use the `test_` prefix to avoid naming conflicts (prevent test folder names from colliding with source module names).
   - `test/integration_test/company_forecast/` → may conflict with the `company_forecast` module
   - `test/integration_test/test_company_forecast/` → clearly separate test code from source code

## Purpose of `conftest.py`

`conftest.py` provides fixtures shared across tests:

- `sample_financial_data`: a standard sample of financial data
- `create_test_company`: factory to create test company folders
- `minimal_inputs`: minimal forecast input data
- `forecast_config`: a standard forecasting configuration
- `model_assumptions`: standard model assumptions

These fixtures avoid duplicating test data setup in each test file.

## Test summary

- **Total tests**: 154
- **Pass rate**: 100% 
- **Unit Tests**: 133
- **Integration Tests**: 21
