"""
StrainFish `predict` CLI interface.

Kranti Konganti
(C) HFP, FDA.
"""

import os
import traceback
from pathlib import Path
from typing import Any, Dict

import rich_click as click
from rich.panel import Panel

from ..constants import SFConstants as SFC
from ..helpers import SFHelpers
from ..logging_utils import console, log, progress
from ..main import strainfish_predict
from ..models import SFModels


# ----------------------------------------------------------------------
# Level 1: Predict command: strainfish predict --help
# ----------------------------------------------------------------------
@click.group(name="predict")
def predict_params() -> None:
    """
    Run StrainFish `predictor` on input DNA Sequences in
    FASTA format or list available trained models.
    """
    pass


# ----------------------------------------------------------------------
# Level 2: Predict group: strainfish predict run --help
# ----------------------------------------------------------------------
@predict_params.command(name="run")
@click.pass_context
@click.option(
    "--fasta",
    "-f",
    required=True,
    help="Input path to FASTA file or path to directory containing FASTA files.",
)
@click.option(
    "--model",
    "-m",
    default=None,
    required=True,
    show_default=True,
    type=click.STRING,
    help=(
        "Perform prediction using this model. Run "
        "`strainfish predict list-models` to show all available models for use."
    ),
)
@click.option(
    "--output",
    "-o",
    default=None,
    show_default=True,
    type=click.Path(file_okay=False, writable=True),
    help="Output directory path to write results in CSV format.",
)
@click.option(
    "--sample-name",
    "-sn",
    default=None,
    show_default=True,
    type=click.STRING,
    help="Optional sample name to include in results file.",
)
@click.option(
    "--xgb-weight",
    "-xw",
    default=SFC.XGBWT_V,
    show_default=True,
    type=click.FloatRange(0.1, 0.99),
    help=(
        "Weight bias for XGBoost predictions during Ensemble probability calculation. "
        "The weight bias for RandomForest predictions will be: 1 - 'XGB Weight Bias'."
    ),
)
@click.option(
    "--threshold",
    "-thr",
    default=SFC.USRTHR,
    show_default=True,
    type=click.FloatRange(0.0, 1.0),
    help="Probability threshold to use when gathering Ensemble predictions.",
)
@click.option(
    "--min-percent",
    "-mp",
    default=SFC.USRMP,
    show_default=True,
    type=click.FloatRange(0.0, 1.0),
    help="Minimum fraction of chunks to consider that pass probability threshold.",
)
@click.option(
    "--encode-method",
    "-em",
    default=SFC.TFIDF,
    show_default=True,
    type=click.STRING,
    help=f"Encoding method to use. Valid options are {SFC.SOMH} or {SFC.SPEC} or {SFC.TFIDF}.",
)
def predict_run(
    ctx: click.Context,
    fasta: os.PathLike,
    model: str,
    output: os.PathLike,
    encode_method: str,
    **hyper_kwargs: Dict[str, Any],
):
    """
    Run StrainFish `predictor` on input DNA sequences in FASTA format.
    """
    console.print(
        Panel.fit(
            "[bold blue]StrainFish Prediction Mode.[/bold blue]\n"
            "Performing prediction using stored models...",
            border_style="blue",
        )
    )

    all_params = ctx.params  # dict

    # Do the prediction
    try:
        strainfish_predict(
            fasta=fasta,
            model=model,
            output=output if output is not None else Path.cwd(),
            encode_method=encode_method,
            all_params=all_params,
        )
    except Exception as e:
        progress.stop()
        e_lines = traceback.format_exception(type(e), e, e.__traceback__)
        for line in e_lines:
            log.error(line.rstrip())


# ----------------------------------------------------------------------
# Level 2: Predict group: strainfish train list-models
# ----------------------------------------------------------------------
@predict_params.command(name="list-models")
@click.option(
    "--models-dir",
    "-md",
    default=None,
    show_default=True,
    type=click.Path(file_okay=False, writable=True),
    help="Search this directory for StrainFish models.",
)
def list_models(models_dir: os.PathLike = None) -> None:
    """List available models that are accessible by StrainFish."""
    SFHelpers._show_pkg_info()
    SFModels.list_models(models_dir)
