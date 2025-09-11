"""
StrainFish Random Forest configuration definitions.

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
class RandomForestConfig:
    """Configuration class for RandomForestClassifier.

    Override any of them on the CLI with the
    --rf- prefix (e.g. --rf-max-depth 15).
    """

    # --------------------------------------------------------
    # 1. General parameters.
    # --------------------------------------------------------
    n_estimators: int = field(
        default=500,
        metadata=_h(
            "Number of trees in the forest. Larger values reduce variance "
            "but increase training time."
        ),
    )
    max_depth: int = field(
        default=10,
        metadata=_h(
            "Maximum depth of each tree. None means nodes are expanded "
            "until all leaves are pure or contain fewer than --rf-min-samples-split."
        ),
    )
    max_features: str = field(
        default="sqrt",
        metadata=_h(
            "Fraction of columns to draw for each split. Ex: 0.6 or 'log2' or 'sqrt'"
        ),
    )
    min_samples_split: int = field(
        default=5,
        metadata=_h(
            "The minimum number of samples required to split an internal node."
        ),
    )
    min_samples_leaf: int = field(
        default=2,
        metadata=_h("The minimum number of samples required to be at a leaf node."),
    )

    # --------------------------------------------------------
    # 2. Weights.
    # --------------------------------------------------------
    bootstrap: bool = field(
        default=True,
        metadata=_h(
            "Whether bootstrap samples are used when building trees. "
            "If False the whole dataset is used to grow each tree."
        ),
    )
    # --------------------------------------------------------
    # Imbalance params
    # --------------------------------------------------------
    smote_enn_s_s: str = field(
        default="not majority",
        metadata=_h("Specifies the resampling strategy for balancing labels."),
    )
    smote_enn_n_jobs: int = field(
        default=20,
        metadata=_h("Number of CPU cores used during the cross-validation loop."),
    )
    smote_k_neighbors: int = field(
        default=5,
        metadata=_h(
            "The nearest neighbors used to define the neighborhood of "
            "samples to use to generate the synthetic samples for SMOTE."
        ),
    )
    enn_n_neighbors: int = field(
        default=3,
        metadata=_h(
            "A sample will be removed when any or most of its enn_n_neighors' "
            "closest neighbours are from a different class."
        ),
    )
    # oob_score: bool = field(
    #     default=False,
    #     metadata=_h("Whether to use OOB samples to estimate the generalisation error."),
    # )
    # class_weight: Optional[Union[dict, List[dict], str]] = field(
    #     default="balanced",
    #     metadata=_h(
    #         "Weights associated with classes. 'balanced' uses the "
    #         "inverse frequency of class labels as weights."
    #     ),
    # )

    # --------------------------------------------------------
    # 3. Other parameters.
    # --------------------------------------------------------
    random_state: int = field(
        default=42,
        metadata=_h("Seed used by the random number generator."),
    )
    n_bins: int = field(
        default=256,
        metadata=_h(
            "Histogram/quantile bin count. Lowering it can speed training at the cost of a little precision."
        ),
    )
    # --------------------------------------------------------
    # CPU params
    # --------------------------------------------------------
    # n_jobs: Optional[int] = field(
    #     default=2,
    #     metadata=_h(
    #         "Number of CPU cores used during training. -1 uses all " "available cores."
    #     ),
    # )
    split_criterion: str = field(
        default="gini",
        metadata=_h(
            "Function to measure the quality of a split. "
            "Supported: 'gini', 'entropy', 'poisson', 'gamma', 'mse' and 'inverse_guassian'."
        ),
    )
    verbose: int = field(
        default=3,
        metadata=_h(
            "Sets logging level. "
            "Set to 0 to silence RandomForestClassifier's own output."
        ),
    )

    # --------------------------------------------------------
    # 4. Return config parameters.
    # --------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Return a nested dictionary suitable for `RandomForest`.
        The outer key 'rf' mirrors the CLI prefix.
        """
        return {"rf": {f.name: getattr(self, f.name) for f in fields(self)}}
