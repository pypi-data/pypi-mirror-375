"""
StrainFish integration tests with real data.

Kranti Konganti
(C) HFP, FDA.
"""

from pathlib import Path

import pytest

from strainfish.cli import strainfish
from strainfish.constants import SFConstants as SFC
from tests.sf_test_helpers import SFTestHelpers

MODEL_NAME = "test_model"
TEST_OUT = "test_output"
TRAIN_DIR = "test_input"


@pytest.fixture(scope="module")
def test_data_dir() -> Path:
    """
    Path to the cronobacter training data directory.

    Returns:
        Path: Path object pointing to the training data directory.
    """
    return Path(__file__).parent / TRAIN_DIR


@pytest.fixture(scope="module")
def output_dir() -> Path:
    """
    Temporary directory for test outputs.

    Args:
        None.

    Returns:
        Path: Path object pointing to a temporary output directory.
    """
    test_out_path = Path(__file__).parent / TEST_OUT
    test_out_path.mkdir(exist_ok=True, parents=True)

    return test_out_path


@pytest.mark.integration
def test_training(test_data_dir: Path, output_dir: Path) -> None:
    cli_runner = SFTestHelpers.get_cli_runner()
    """
    Test the full training command with real data.
    
    This integration test verifies that the complete StrainFish training pipeline
    can be executed successfully using actual cronobacter training data. It tests
    data loading, preprocessing, model training, and file generation.

    The method uses Click's CliRunner to directly invoke the CLI commands,
    providing more reliable testing without subprocess dependencies.

    Command tested:
        strainfish train run -f test_input/test.train.fasta \
            -l test_input/test.train.csv -o test_output/test_model
    
    Args:
        cli_runner (CliRunner): Click testing runner.
        test_data_dir (Path): Path to the training data directory.
        output_dir (Path): Temporary directory for saving model outputs.
        
    Raises:
        ValueError: If input files are missing or parameters are invalid.
    
    Note:
        This test requires real cronobacter training data and may take time
        to complete depending on dataset size and system capabilities.
    """
    fasta_file = test_data_dir / "test.train.fasta"
    label_file = test_data_dir / "test.train.csv"

    if not fasta_file.exists():
        pytest.skip(f"FASTA file not found: {fasta_file}")

    if not label_file.exists():
        pytest.skip(f"Label file not found: {label_file}")

    # Use CliRunner to invoke the command
    result = cli_runner.invoke(
        strainfish,
        [
            "train",
            "run",
            "-f",
            str(fasta_file),
            "-l",
            str(label_file),
            "-o",
            str(Path(output_dir, MODEL_NAME)),
        ],
    )

    # Check that the command executed successfully
    assert (
        result.exit_code == 0
    ), f"Training failed with output: {result.output}\n{result.exception}"

    # Verify that expected model files were created
    # At present default encoding: TFIDF
    expected_files = [
        MODEL_NAME + SFC.XGB_SUFFIX,
        MODEL_NAME + SFC.RF_SUFFIX,
        MODEL_NAME + SFC.NB_SUFFIX,
        MODEL_NAME + SFC.LBL_SUFFIX,
        MODEL_NAME + SFC.TF_CRPS_SUFFIX,
    ]

    for filename in expected_files:
        model_file = output_dir / filename
        assert model_file.exists(), f"Expected model file not found: {model_file}"


@pytest.mark.integration
def test_prediction(test_data_dir: Path, output_dir: Path) -> None:
    cli_runner = SFTestHelpers.get_cli_runner()
    """
    Test the prediction command with a trained model.
    
    This integration test verifies that StrainFish can successfully load
    a trained model and perform predictions on new sequence data. It tests
    model loading, preprocessing, and inference functionality.

    The method uses Click's CliRunner to directly invoke the CLI commands,
    providing more reliable testing without subprocess dependencies.

    Command tested:
        strainfish predict -m /path/to/trained/model \
            -f /path/to/test_sequences.fasta
    
    Args:
        cli_runner (CliRunner): Click testing runner.
        test_data_dir (Path): Path to the training data directory for test sequences.
        output_dir (Path): Directory containing trained model files.
        
    Note:
        This test depends on successful completion of the training test,
        as it uses the models generated during training. It reuses a subset
        of the cronobacter training data for prediction testing.
    """
    # Skip if training didn't produce expected models
    model_file_prefix = Path(output_dir, MODEL_NAME)
    model_files = list(Path(output_dir).glob(f"{MODEL_NAME}*"))
    if len(model_files) == 0:
        pytest.skip("Training models not found - skipping prediction test")

    # Use a subset of training data for testing predictions
    test_fasta = test_data_dir / "predict.fasta"

    if not test_fasta.exists():
        pytest.skip(f"Test FASTA file not found: {test_fasta}")

    # Use CliRunner to invoke the command
    result = cli_runner.invoke(
        strainfish,
        [
            "predict",
            "run",
            "-m",
            str(model_file_prefix),
            "-f",
            str(test_fasta),
            "-o",
            str(output_dir),
        ],
    )

    # Check that the command executed successfully
    assert (
        result.exit_code == 0
    ), f"Prediction failed with output: {result.output}\n{result.exception}"

    # Verify that prediction output contains expected information
    # output_text = result.output.lower()
    # assert (
    #     "predictions" in output_text or "results" in output_text
    # ), f"Expected 'predictions' or 'results' in output, got: {output_text}"

    # Check for the presence of StrainFish_results.csv file
    results_file = Path(output_dir) / "StrainFish_results.csv"
    assert results_file.exists(), f"StrainFish_results.csv not found in {output_dir}"

    # Verify that the CSV file contains exactly a header row and one result row with 'predict' as sample name
    with open(results_file, "r") as f:
        lines = f.readlines()

    # Check for header row (at least 2 columns)
    assert len(lines) >= 1, "CSV file should have at least a header row"
    headers = lines[0].strip().split(",")
    assert (
        len(headers) >= 2
    ), f"Header row should have at least 2 columns, got: {len(headers)}"

    # Check for result row
    assert (
        len(lines) == 2
    ), f"CSV file should have exactly 2 rows (header + data), got: {len(lines)}"
    sample_name = lines[1].strip().split(",")[0]
    assert (
        sample_name == "predict"
    ), f"Expected sample name to be 'predict', got: '{sample_name}'"
