"""
StrainFish XGBoost configuration definitions.

Kranti Konganti
(C) HFP, FDA.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, Dict


def _h(msg: str) -> dict:
    """
    Create metadata dictionary with help text for Click option generation.

    This internal helper function serves as a convenient shortcut for creating
    metadata dictionaries that are used by the dynamic CLI parameter system.
    It standardizes how help messages are attached to dataclass fields,
    ensuring consistent formatting and behavior across all configuration classes.
    The returned dictionary is automatically processed by the CLI builder to
    generate properly formatted command-line options.

    Args:
        msg (str): The help message text that will be associated with a
            configuration parameter. This text should describe the purpose,
            usage, or constraints of the corresponding configuration field.

    Returns:
        dict: A dictionary containing a single 'help' key with the provided
            message as its value. This metadata is used by Click decorators
            to generate command-line help text for each configuration option.

    Raises:
        None: This function accepts any string input and returns a predictable
            dictionary structure, making it safe to use in all contexts.
    """
    return {"help": msg}


@dataclass
class XGBoostConfig:
    """Configuration class for XGBoost parameters.

    Override any of them on the CLI with the
    --xgb- prefix (e.g. --xgb-max-depth 12).
    """

    # --------------------------------------------------------
    # 1. General parameters.
    # --------------------------------------------------------
    nthread: int = field(
        default=2,
        metadata=_h(
            "Number of CPU threads XGBoost may use. " "Ignored when device='cuda'."
        ),
    )
    device: str = field(
        default="cuda",
        metadata=_h(
            "Device on which training runs. "
            "Supported values: 'cpu' or 'cuda'. "
            "When 'cuda' is chosen the GPU version of the "
            "histogram algorithm is used."
        ),
    )

    # --------------------------------------------------------
    # 2. Booster specific parameters.
    # --------------------------------------------------------
    eta: float = field(
        default=0.1,
        metadata=_h(
            "Learning rate (shrinkage). Smaller values make training "
            "more robust but require more boosting rounds."
        ),
    )
    gamma: float = field(
        default=0.0,
        metadata=_h(
            "Minimum loss reduction required to make a further partition "
            "on a leaf node of the tree."
        ),
    )
    max_depth: int = field(
        default=10,
        metadata=_h(
            "Maximum depth of a tree. Deeper trees can capture more "
            "complex interactions but risk over fitting."
        ),
    )
    min_child_weight: float = field(
        default=1.0,
        metadata=_h(
            "Minimum sum of instance weight (hessian) needed in a child. "
            "Larger values make the algorithm more conservative."
        ),
    )
    max_delta_step: float = field(
        default=1.0,
        metadata=_h(
            "Maximum delta step we allow each leaf output to be. "
            "Usually only needed for imbalanced logistic regression."
        ),
    )
    subsample: float = field(
        default=1.0,
        metadata=_h(
            "Fraction of the training data to sample for each boosting "
            "iteration. Typical values are in [0.5, 1.0]."
        ),
    )
    colsample_bytree: float = field(
        default=0.8,
        metadata=_h("Fraction of features (columns) to sample for each tree."),
    )
    colsample_bynode: float = field(
        default=1.0,
        metadata=_h(
            "Fraction of features to sample for each split node. "
            "Keeps the per node feature space small."
        ),
    )
    reg_alpha: float = field(
        default=0.0,
        metadata=_h("L1 regularisation term on weights (analogous to Lasso)."),
    )
    reg_lambda: float = field(
        default=1.0,
        metadata=_h("L2 regularisation term on weights (analogous to Ridge)."),
    )
    tree_method: str = field(
        default="hist",
        metadata=_h("Tree construction algorithm."),
    )
    max_leaves: int = field(
        default=0,
        metadata=_h(
            "Maximum number of leaves per tree. 0 means no limit (the default)."
        ),
    )

    # --------------------------------------------------------
    # 3. Objective & evaluation.
    # --------------------------------------------------------
    objective: str = field(
        default="multi:softprob",
        metadata=_h(
            "Learning objective. 'multi:softprob' returns class "
            "probabilities for multi-class classification."
        ),
    )
    imbal_class_weight: str = field(
        default="balanced",
        metadata=_h(
            "Weights associated with labels in the form {label: weight}. "
            "The 'balanced' mode uses the values of vector to automatically"
            " adjust weights inversely proportional to label frequencies."
        ),
    )
    eval_metric: str = field(
        default="mlogloss",
        metadata=_h(
            "Metric used for early stopping and evaluation. "
            "'mlogloss' is the multiclass logloss."
        ),
    )
    seed: int = field(
        default=42,
        metadata=_h("Random seed for reproducibility."),
    )

    # --------------------------------------------------------
    # 4. Training parameters.
    # --------------------------------------------------------
    num_boost_round: int = field(
        default=5000,
        metadata=_h(
            "Maximum number of boosting iterations (trees). "
            "Early stopping may terminate earlier."
        ),
    )
    early_stopping_rounds: int = field(
        default=1000,
        metadata=_h(
            "Stop training if the validation score does not improve "
            "for this many rounds. Set to 0 to disable."
        ),
    )
    verbose_eval: int = field(
        default=500,
        metadata=_h(
            "How often (in boosting rounds) to print a progress line. "
            "Set to 0 to silence XGBoost's own output."
        ),
    )

    # --------------------------------------------------------
    # 5. Return config parameters.
    # --------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the dataclass into the nested dictionary format expected
        by `XGBoost`. The outer key 'xgb' mirrors the prefix used by the
        Click wrapper.
        """
        return {"xgb": {f.name: getattr(self, f.name) for f in fields(self)}}
