"""
StrainFish models' helper class to list and return models' paths.

Kranti Konganti
(C) HFP, FDA.
"""

import os
import re
from collections import Counter
from pathlib import Path
from typing import List, Optional, Tuple

from rich import box
from rich.panel import Panel
from rich.table import Table as T

from .constants import SFConstants as SFC
from .logging_utils import console, log


class SFModels:
    """
    StrainFish model management and utilities class.

    This class provides static methods for managing trained machine learning models,
    including listing available models, checking ensemble model agreement, and
    retrieving specific model file paths. It handles XGBoost, RandomForest, Naive Bayes,
    SentencePiece, and label files as part of the complete StrainFish model ecosystem.
    """

    @staticmethod
    def check_ensemble_model_agreement(
        labels: Optional[List[str]],
    ) -> Tuple[List[int], str]:

        if labels is None:
            log.error("Cannot lookup labels since it is None!")
            raise TypeError()

        # Count frequency of each label
        label_counts = Counter(labels)
        max_count = max(label_counts.values())

        match max_count:
            # All the model predictions agree
            case 3:
                return [0, 1, 2], labels[0]
            # Only two of the models agree
            case 2:
                majority_voted = label_counts.most_common(1)[0][0]
                agreeing_model_idxs = [
                    i for i, label in enumerate(labels) if label == majority_voted
                ]
                return agreeing_model_idxs, labels[agreeing_model_idxs[0]]
            # Return XGBoost if none of the models agree. Empirical testing shows
            # XGBoost performs well over RF and NB. 0 is always XGBoost.
            case _:
                return [0], labels[0]

    @staticmethod
    def list_models(
        models_dir: Optional[os.PathLike] = None, get_this_model: Optional[str] = None
    ) -> Optional[Tuple[os.PathLike, os.PathLike, os.PathLike, os.PathLike]]:
        """
        Show a table of all XGBoost/RandomForest model pairs that exist
        in *models_dir*.  If *get_this_model* is supplied, the function
        returns the paths for that pair immediately.

        Args:
            models_dir : PathLike, optional
                Directory that contains the model files.  Defaults to
                :data:`MODELS_DIR`.
            get_this_model : str, optional
                The *base* name (without suffixes) of a particular model.
                If supplied, the function returns `(xgb_path, rf_path)`
                for that model instead of printing the table.

        Returns:
            tuple[Path, Path, Path] | None
                The three paths if *get_this_model* was supplied and matched;
                otherwise `None`.
        """
        table = T(
            box=box.ROUNDED,
            border_style="dim white",
            show_edge=False,
            show_lines=False,
        )

        if models_dir is None:
            models_dir = SFC.MODELS_DIR

        table.add_column("Model", style="cyan")
        models = list(Path(models_dir).glob(f"*{SFC.XGB_SUFFIX}"))

        if len(models) == 0:
            table.add_row(f"No models found in directory: [red]{models_dir}[/red].")
        else:
            model_names = [
                re.sub(SFC.XGB_SUFFIX, "", os.path.basename(str(m_file)))
                for m_file in models
            ]
            model_map = {v: i + 1 for i, v in enumerate(model_names)}

            if model_map.get(get_this_model, None):
                x_name = get_this_model + SFC.XGB_SUFFIX
                r_name = get_this_model
                r_path = os.path.join(models_dir, r_name + SFC.RF_SUFFIX)
                n_path = os.path.join(models_dir, r_name + SFC.NB_SUFFIX)
                l_path = os.path.join(models_dir, r_name + SFC.LBL_SUFFIX)
                s_path = os.path.join(
                    models_dir, r_name + SFC.SP_CRPS_SUFFIX + SFC.SP_C_CRPS_SUFFIX
                )
                t_path = os.path.join(models_dir, r_name + SFC.TF_CRPS_SUFFIX)
                x_path = os.path.join(models_dir, x_name)

                if not os.path.exists(r_path):
                    log.error(
                        (
                            "A corresponding RandomForest model does not"
                            f" exist for {re.sub(SFC.XGB_SUFFIX, '', x_name)}."
                            f"\nRF: {r_path}"
                        )
                    )
                    raise FileNotFoundError()

                if not os.path.exists(n_path):
                    log.error(
                        (
                            "A corresponding Naive Bayes model does not"
                            f" exist for {re.sub(SFC.XGB_SUFFIX, '', x_name)}."
                            f"\nRF: {n_path}"
                        )
                    )
                    raise FileNotFoundError()

                if not os.path.exists(l_path):
                    log.error(
                        (
                            "A corresponding Labels vector does not"
                            f" exist for {re.sub(SFC.XGB_SUFFIX, '', x_name)}."
                            f"\nLBL: {l_path}"
                        )
                    )
                    raise FileNotFoundError()

                return x_path, r_path, l_path, s_path, t_path, n_path

            elif (
                get_this_model is not None
                and model_map.get(get_this_model, None) is None
            ):
                log.error(
                    (
                        f"Model [bold cyan]{get_this_model}[/bold cyan] not"
                        f" found in directory: [red]{models_dir}[/red]!"
                    )
                )
                raise FileNotFoundError()

            for m_name in model_names:
                table.add_row(m_name)

        console.print(
            "\n",
            Panel.fit(
                table,
                title="Available StrainFish Models",
                title_align="left",
                border_style="turquoise2",
                padding=(1, 1, 1, 1),
            ),
        )

        return [None] * 6
