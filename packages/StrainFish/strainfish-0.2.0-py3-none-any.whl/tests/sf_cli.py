"""
StrainFish CLI tests.

Kranti Konganti
(C) HFP, FDA.
"""

import pytest

from strainfish.cli import strainfish
from tests.sf_test_helpers import SFTestHelpers

cli_runner = SFTestHelpers.get_cli_runner()


@pytest.mark.unit
def test_help_command() -> None:
    """
    Test that the main help command works and exits with code 0.

    This test verifies that the base `strainfish` command can be executed
    without errors and returns appropriate output containing usage information.

    Note:
        This is a basic smoke test that verifies the CLI entry point is functional.
    """
    result = cli_runner.invoke(strainfish, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output.lower() or "strainfish" in result.output.lower()


@pytest.mark.unit
def test_train_command() -> None:
    """
    Test that the `train` subcommand works and exits with code 0.

    This test verifies that the `strainfish train` command can be executed
    without errors, indicating proper CLI setup and command registration.

    Note:
        This test ensures that all training-related CLI commands are properly
        configured before testing specific training operations.
    """
    result = cli_runner.invoke(strainfish, ["train", "--help"])
    assert result.exit_code == 0


@pytest.mark.unit
def test_train_run_command() -> None:
    """
    Test that the `train run` subcommand works and exits with code 0.

    This test verifies that the `strainfish train run` command can be executed
    without errors. Since no arguments are provided, it should show help
    or usage information indicating required parameters.

    Note:
        This test expects a help message since no required parameters are provided,
        which aligns with the validation pattern used in `SFTrainer.train()`.
    """
    result = cli_runner.invoke(strainfish, ["train", "run", "--help"])
    assert result.exit_code == 0

    # Should show help or usage for train run since no args provided
    assert "usage:" in result.output.lower() or "options" in result.output.lower()


@pytest.mark.unit
def test_show_xgb_params_command() -> None:
    """
    Test that the `show-xgb-params` command works and exits with code 0.

    This test verifies that the `strainfish train show-xgb-params` command can be
    executed without errors, indicating proper parameter display functionality.

    Note:
        This test ensures that users can access default XGBoost parameters,
        which helps in understanding the expected parameter structure for training.
    """
    result = cli_runner.invoke(strainfish, ["train", "show-xgb-params"])
    assert result.exit_code == 0


@pytest.mark.unit
def test_train_show_rf_params_command() -> None:
    """
    Test that the `strainfish train show-rf-params` command works and exits with code 0.

    This test verifies that the `strainfish train show-rf-params` command can be
    executed without errors, indicating proper random forest parameter display functionality.

    Note:
        This test ensures that users can access default RandomForest parameters,
        which helps in understanding the expected parameter structure for training.
    """
    result = cli_runner.invoke(strainfish, ["train", "show-rf-params"])
    assert result.exit_code == 0


@pytest.mark.unit
def test_train_show_sp_params_command() -> None:
    """
    Test that the `strainfish train show-sp-params` command works and exits with code 0.

    This test verifies that the `strainfish train show-sp-params` command can be
    executed without errors, indicating proper SentencePiece parameter display functionality.

    Note:
        This test ensures that users can access default SentencePiece parameters,
        which helps in understanding the expected parameter structure for training
        with the SPEC encoding method.
    """
    result = cli_runner.invoke(strainfish, ["train", "show-sp-params"])
    assert result.exit_code == 0


@pytest.mark.unit
def test_train_show_imb_params_command() -> None:
    """
    Test that the `strainfish train show-imb-params` command works and exits with code 0.

    This test verifies that the `strainfish train show-imb-params` command can be
    executed without errors, indicating proper imbalance parameter display functionality.

    Note:
        This test ensures that users can access default imbalance parameters,
        which helps in understanding how to configure data balancing strategies.
    """
    result = cli_runner.invoke(strainfish, ["train", "show-imb-params"])
    assert result.exit_code == 0


@pytest.mark.unit
def test_predict_command() -> None:
    """
    Test that the `predict` subcommand works and exits with code 0.

    This test verifies that the `strainfish predict` command can be executed
    without errors, indicating proper CLI setup for prediction functionality.

    Note:
        This test ensures that all prediction-related CLI commands are properly
        configured before testing specific prediction operations.
    """
    result = cli_runner.invoke(strainfish, ["predict", "--help"])
    assert result.exit_code == 0


@pytest.mark.unit
def test_predict_list_models_command() -> None:
    """
    Test that the `predict list-models` command works and exits with code 0.

    This test verifies that the `strainfish predict list-models` command can be
    executed without errors, indicating proper model listing functionality.

    Note:
        This test ensures that users can discover available trained models,
        which helps in understanding what models are ready for prediction tasks.
    """
    result = cli_runner.invoke(strainfish, ["predict", "list-models"])
    assert result.exit_code == 0
