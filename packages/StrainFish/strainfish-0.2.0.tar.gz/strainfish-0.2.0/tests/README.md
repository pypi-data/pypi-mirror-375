# StrainFish Tests

This directory contains tests for the StrainFish application. The tests are organized into two main categories:

## Test Categories

### Unit Tests (`sf_cli.py`)

These tests verify that all CLI subcommands work correctly and exit with code 0.

**Commands Tested:**

- `strainfish` (shows default help menu)
- `strainfish train`
- `strainfish train run`
- `strainfish show-xgb-params`
- `strainfish predict`
- `strainfish predict list-models`

### Integration Tests (`sf_integration.py`)

These tests verify the end-to-end functionality of StrainFish with real data.

**Tests Included:**

1. **Training Test**: Runs a full training pipeline using test data from `tests/test_input`

    - `strainfish train run -f tests/test_input/test.train.fasta -l tests/test_input/test.train.csv -o tests/test_output/test_model`

2. **Prediction Test**: Runs prediction on trained model from `tests/test_output/test_model.*`

    - `strainfish predict run -f tests/test_input/predict.fasta -m tests/test_output/test_model`

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Only Unit Tests

```bash
pytest -m unit
```

### Run Only Integration Tests

```bash
pytest -m integration
```

### Run with Coverage

```bash
pytest --cov=src/strainfish
```

## Test Data

Integration tests use data from:

- `tests/test_input/test.train.fasta`
- `tests/test_input/test.train.csv`
- `tests/test_input/predict.fasta`

## Test Configuration

Tests are configured in:

- `pytest.ini`: Pytest configuration
- `.gitignore`: Excludes test files from version control
- `pyproject.toml`: Excludes tests from package distribution

## Notes

1. Integration tests will be skipped if the required test data is not found.
2. All tests uses `CliRunner` to execute commands, ensuring they run in the correct environment.
3. Test outputs are written to temporary directories that are automatically cleaned up.
