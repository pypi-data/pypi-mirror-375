"""
StrainFish: An Ensemble Machine Learning algorithm for classification of bacterial strains.

Kranti Konganti
(C) HFP, FDA.
"""

import os
import time
import traceback
from dataclasses import asdict, fields
from typing import Dict

from .configs import (
    ImbalanceConfig,
    RandomForestConfig,
    SentencePieceConfig,
    XGBoostConfig,
)
from .constants import SFConstants as SFC
from .dynamic_cli_params import build_params
from .helpers import SFHelpers
from .logging_utils import log, progress
from .predictor import SFPredictor
from .trainer import SFTrainer

# ----------------------------------------------------------------------
# 1. Start timer
# ----------------------------------------------------------------------
start = time.time()


# ----------------------------------------------------------------------
# 2. The actual training routine – all heavy lifting
# ----------------------------------------------------------------------
def strainfish_train(
    fasta: os.PathLike,
    labels: os.PathLike,
    output_dir: os.PathLike,
    encode_method: str,
    kmer: int,
    n_hashes: int,
    factor: int,
    chunk_size: int,
    pseknc_weight: float,
    xgb_params: Dict,
    rf_params: Dict,
    sp_params: Dict,
    imb_params: Dict,
    all_params: Dict,
) -> None:
    """
    Run XGBoost and RandomForest training on input FASTA according to
    StrainFish algorithm.
    """

    # Build the config objects (with validation)
    xgb_cfg = build_params(XGBoostConfig, xgb_params, SFC.XGB_PREFIX_U)
    rf_cfg = build_params(RandomForestConfig, rf_params, SFC.RF_PREFIX_U)
    sp_cfg = build_params(SentencePieceConfig, sp_params, SFC.SP_PREFIX_U)
    imb_cfg = build_params(ImbalanceConfig, imb_params, SFC.IMB_PREFIX_U)

    # Log all parameters
    log.info("[green3]Global parameters[/green3]")
    key_len = max(len(k) for k in all_params.keys())
    for k, v in all_params.items():
        if k in list(
            set(
                list(xgb_params.keys())
                + list(rf_params.keys())
                + list(sp_params.keys())
                + list(imb_params.keys())
            )
        ):
            continue
        if v is not None:
            log.info(
                f"[slate_blue1]{k:<{key_len}}[/slate_blue1]: [bold cyan]{v}[bold /cyan]"
            )

    # Log SentencePiece parameters
    if encode_method == SFC.SPEC:
        log.info("[green3]SentencePiece parameters[/green3]")
        disp_cfg = fields(sp_cfg)
        for f in disp_cfg:
            log.info(
                f"[slate_blue1]{f.name:<{key_len}}[/slate_blue1]: {getattr(sp_cfg, f.name)}"
            )

    # Log XGBoost parameters
    log.info("[green3]XGBoost parameters[/green3]")
    disp_cfg = fields(xgb_cfg)
    for f in disp_cfg:
        log.info(
            f"[slate_blue1]{f.name:<{key_len}}[/slate_blue1]: {getattr(xgb_cfg, f.name)}"
        )

    # Log RandomForest parameters
    log.info("[green3]RandomForest parameters[/green3]")
    disp_cfg = fields(rf_cfg)
    for f in disp_cfg:
        log.info(
            f"[slate_blue1]{f.name:<{key_len}}[/slate_blue1]: {getattr(rf_cfg, f.name)}"
        )

    # Log Imbalance parameters
    log.info("[green3]Imbalance parameters[/green3]")
    disp_cfg = fields(imb_cfg)
    for f in disp_cfg:
        log.info(
            f"[slate_blue1]{f.name:<{key_len}}[/slate_blue1]: {getattr(imb_cfg, f.name)}"
        )

    # Do the StrainFish training
    try:
        sf_trainer = SFTrainer(
            fasta_file=fasta,
            label_file=labels,
            encode_method=encode_method,
            n_hashes=n_hashes,
            k=kmer,
            factor=factor,
            chunk_size=chunk_size,
            pseknc_weight=pseknc_weight,
            save_prefix=output_dir,
            xgb_params=asdict(xgb_cfg),
            rf_params=asdict(rf_cfg),
            sp_params=asdict(sp_cfg),
            imb_params=asdict(imb_cfg),
        )
        sf_trainer.train()
    except Exception as e:
        progress.stop()
        e_lines = traceback.format_exception(type(e), e, e.__traceback__)
        for line in e_lines:
            log.error(line.rstrip())
    else:
        end = time.time()
        log.info(
            (
                "[green3]Training completed in [/green3][bold cyan]"
                f"{SFHelpers._elapsed_time(start=start, end=end)}[/bold cyan]."
            )
        )
        log.info(
            (
                "[green3]Use `[bold cyan]strainfish predict[/bold cyan]`"
                " to do your predictions![/green3]"
            )
        )


def strainfish_predict(
    fasta: os.PathLike,
    model: str,
    output: os.PathLike,
    encode_method: str,
    all_params: Dict,
) -> None:
    """
    Run StrainFish prediction on input FASTA seqeunces according to
    StrainFish algorithm.
    """
    # Log params
    SFHelpers._log_params(all_params)

    # Do the StrainFish prediction
    try:
        sf_predict = SFPredictor(
            fasta_file=fasta,
            model=model,
            output=output,
            encode_method=encode_method,
            all_params=all_params,
        )
        sf_predict.predict()
    except Exception as e:
        progress.stop()
        e_lines = traceback.format_exception(type(e), e, e.__traceback__)
        for line in e_lines:
            log.error(line.rstrip())
    else:
        end = time.time()
        log.info(
            (
                "[green3]Prediction completed in [/green3][bold cyan]"
                f"{SFHelpers._elapsed_time(start=start, end=end)}[/bold cyan]."
            )
        )
        log.info(
            (
                "[green3]`[bold cyan]strainfish[/bold cyan]` prediction complete!"
                " Happy exploration of results![/green3]"
            )
        )
