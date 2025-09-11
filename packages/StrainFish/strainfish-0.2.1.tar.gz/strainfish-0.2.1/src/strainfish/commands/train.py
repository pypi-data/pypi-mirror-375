"""
StrainFish `train` CLI interface.

Kranti Konganti
(C) HFP, FDA.
"""

import os
import traceback
from typing import Any, Dict

import rich_click as click
from rich.panel import Panel

from ..configs import (
    ImbalanceConfig,
    RandomForestConfig,
    SentencePieceConfig,
    XGBoostConfig,
)
from ..constants import SFConstants as SFC
from ..dynamic_cli_params import add_params_from_dataclass, fields2table
from ..helpers import SFHelpers
from ..logging_utils import console, log
from ..main import strainfish_train


# ----------------------------------------------------------------------
# Level 1: Train group: strainfish train --help
# ----------------------------------------------------------------------
@click.group(name="train")
def train_params() -> None:
    """
    Run StrainFish `trainer` algorithm on input DNA Sequences in
    FASTA format.
    """
    pass


# ----------------------------------------------------------------------
# Level 2: Train group: strainfish train run --help
# ----------------------------------------------------------------------
@train_params.command(name="run")
@click.pass_context
@click.option("--fasta", "-f", required=True, help="Input path to FASTA file.")
@click.option(
    "--labels",
    "-l",
    required=True,
    type=click.Path(file_okay=True, writable=False),
    help='A 2-column labels file in CSV format where column names are "id" and "label".',
)
@click.option(
    "--output",
    "-o",
    default=None,
    show_default=True,
    type=click.Path(file_okay=False, writable=True),
    help="Output directory path to store model files.",
)
@click.option(
    "--encode-method",
    "-em",
    default=SFC.TFIDF,
    show_default=True,
    type=click.STRING,
    help=f"Encoding method to use. Valid options are '{SFC.SOMH}', '{SFC.SPEC}' or '{SFC.TFIDF}'.",
)
@click.option(
    "--kmer",
    "-k",
    default=SFC.DKMER,
    show_default=True,
    type=click.INT,
    help="The size of k-mer for hashing.",
)
@click.option(
    "--num-hashes",
    "-nh",
    default=SFC.NH,
    show_default=True,
    type=click.INT,
    help=(
        f"Number of hashes per DNA sequence. Ignored for {SFC.SPEC} DNA encoding methods."
        f"For {SFC.TFIDF} encoding method, this limits the features to this number."
    ),
)
@click.option(
    "--factor",
    "-fc",
    default=SFC.FC,
    show_default=True,
    type=click.INT,
    help=(
        "Factor used to calculate sequence overlap. "
        f"Ignored for {SFC.TFIDF} DNA encoding method."
    ),
)
@click.option(
    "--chunk-size",
    "-cs",
    default=SFC.CHKS,
    show_default=True,
    type=click.INT,
    help="Size of each DNA sequence chunk.",
)
@click.option(
    "--pseknc-weight",
    "-pw",
    default=SFC.PSEKNC_W,
    show_default=True,
    type=click.FLOAT,
    help=(
        f"Weight factor for PseKNC during {SFC.SOMH} DNA encoding method. "
        f"Ignored for {SFC.SPEC} and {SFC.TFIDF} DNA encoding methods."
    ),
)
# ---- XGBoost options (prefixed with `xgb-`) ---------------------------------
@add_params_from_dataclass(XGBoostConfig, prefix=f"{SFC.XGB_PREFIX}-")
# ---- RandomForest options (prefixed with `rf-`) -----------------------------
@add_params_from_dataclass(RandomForestConfig, prefix=f"{SFC.RF_PREFIX}-")
# ---- SentencePiece options (prefixed with `sp-`) -----------------------------
@add_params_from_dataclass(SentencePieceConfig, prefix=f"{SFC.SP_PREFIX}-")
# ---- Imbalance options (prefixed with `imb-`) -----------------------------
@add_params_from_dataclass(ImbalanceConfig, prefix=f"{SFC.IMB_PREFIX}-")
# @click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def train_run(
    ctx: click.Context,
    fasta: os.PathLike,
    labels: os.PathLike,
    output: os.PathLike,
    encode_method: str,
    kmer: int,
    num_hashes: int,
    factor: int,
    chunk_size: int,
    pseknc_weight: float,
    **hyper_kwargs: Dict[str, Any],
):
    """Run StrainFish `trainer` on input FASTA sequences."""
    console.print(
        Panel.fit(
            "[bold blue]StrainFish Training Mode.[/bold blue]\n"
            "Analyzing strain patterns and storing models...",
            border_style="blue",
        )
    )

    all_params = ctx.params  # dict

    # xgb_params = {k: v for k, v in all_params.items() if k.startswith(XGB_PREFIX_U)}
    # rf_params = {k: v for k, v in all_params.items() if k.startswith(RF_PREFIX_U)}

    # Split the user params back into two dictionaries
    xgb_params = {
        k: v for k, v in hyper_kwargs.items() if k.startswith(SFC.XGB_PREFIX_U)
    }
    rf_params = {k: v for k, v in hyper_kwargs.items() if k.startswith(SFC.RF_PREFIX_U)}
    sp_params = {k: v for k, v in hyper_kwargs.items() if k.startswith(SFC.SP_PREFIX_U)}
    imb_params = {
        k: v for k, v in hyper_kwargs.items() if k.startswith(SFC.IMB_PREFIX_U)
    }

    # Do the training
    try:
        strainfish_train(
            fasta=fasta,
            labels=labels,
            output_dir=output,
            encode_method=encode_method,
            kmer=kmer,
            n_hashes=num_hashes,
            chunk_size=chunk_size,
            pseknc_weight=pseknc_weight,
            factor=factor,
            xgb_params=xgb_params,
            rf_params=rf_params,
            sp_params=sp_params,
            imb_params=imb_params,
            all_params=all_params,
        )
    except Exception as e:
        e_lines = traceback.format_exception(type(e), e, e.__traceback__)
        for line in e_lines:
            log.error(line.rstrip())


# ----------------------------------------------------------------------
# Level 2: Train group: strainfish train show-xgb-params
# ----------------------------------------------------------------------
@train_params.command(name="show-xgb-params")
def show_xgb_params() -> None:
    """Display every configurable XGBoost parameters."""
    SFHelpers._show_pkg_info()
    console.print(
        "\n",
        Panel.fit(
            fields2table(XGBoostConfig, "XGBoost", SFC.XGB_PREFIX),
            title="XGBoost Parameters",
            title_align="left",
            border_style="blue",
            padding=(1, 1, 1, 1),
        ),
    )


# ----------------------------------------------------------------------
# Level 2: Train group: strainfish train show-rf-params
# ----------------------------------------------------------------------
@train_params.command(name="show-rf-params")
def show_rf_params() -> None:
    """Display every configurable RandomForest parameters."""
    SFHelpers._show_pkg_info()
    console.print(
        "\n",
        Panel.fit(
            fields2table(RandomForestConfig, "RandomForest", SFC.RF_PREFIX),
            title="RandomForest Parameters",
            title_align="left",
            border_style="green",
            padding=(1, 1, 1, 1),
        ),
    )


# ----------------------------------------------------------------------
# Level 2: Train group: strainfish train show-sp-params
# ----------------------------------------------------------------------
@train_params.command(name="show-sp-params")
def show_sp_params() -> None:
    """Display every configurable SentencePiece parameters."""
    SFHelpers._show_pkg_info()
    console.print(
        "\n",
        Panel.fit(
            fields2table(SentencePieceConfig, "SentencePiece", SFC.SP_PREFIX),
            title="SentencePiece Parameters",
            title_align="left",
            border_style="green",
            padding=(1, 1, 1, 1),
        ),
    )


# ----------------------------------------------------------------------
# Level 2: Train group: strainfish train show-imb-params
# ----------------------------------------------------------------------
@train_params.command(name="show-imb-params")
def show_imb_params() -> None:
    """Display every configurable Imbalance parameters."""
    SFHelpers._show_pkg_info()
    console.print(
        "\n",
        Panel.fit(
            fields2table(ImbalanceConfig, "Imbalance", SFC.IMB_PREFIX),
            title="Imbalance Parameters",
            title_align="left",
            border_style="green",
            padding=(1, 1, 1, 1),
        ),
    )
