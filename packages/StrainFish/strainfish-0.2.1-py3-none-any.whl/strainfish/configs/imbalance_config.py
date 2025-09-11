"""
Imbalance configuration definitions.

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
class ImbalanceConfig:
    """Configuration class for Imbalance parameters.

    Override any of them on the CLI with the
    --imb- prefix (e.g. --imb-smote-enn-s-s auto).
    """

    # --------------------------------------------------------
    # 1. Imbalance params
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

    # --------------------------------------------------------
    # 4. Return config parameters.
    # --------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Return a nested dictionary suitable for `ImbalanceConfig`.
        The outer key 'imb' mirrors the CLI prefix.
        """
        return {"imb": {f.name: getattr(self, f.name) for f in fields(self)}}
