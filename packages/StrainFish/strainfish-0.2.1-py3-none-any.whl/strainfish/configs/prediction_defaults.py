"""
StrainFish default prediction configuration definitions.

Kranti Konganti
(C) HFP, FDA.
"""

import logging
from dataclasses import dataclass, field

from ..constants import SFConstants as SFC


@dataclass
class PredictionResult:
    """
    Data Class container for prediction defaults.

    All fields default to `NOPRED`.  The class is mutable so
    you can update fields after a successful prediction.

    Args:
        predicted : Any
            The predicted label (e.g. species name).
        weighted_prob : Any
            Weighted probability for the prediction.
        weighted_support : Any
            Weighted support (e.g. supporting read count).
        confidence : Any
            Confidence score for the prediction.
        num_agreed : Any
            Number of models that agreed on the results.
    """

    predicted: str = field(
        default=SFC.NOPRED, metadata={"msg": "Predicted genome label."}
    )
    weighted_prob: float = field(
        default=SFC.NOPRED, metadata={"msg": "Weighted probability of the prediction."}
    )
    weighted_support: float = field(
        default=SFC.NOPRED, metadata={"msg": "Weighted support (e.g., read count)."}
    )
    confidence: str = field(
        default=SFC.NOPRED, metadata={"msg": "Confidence score for the prediction."}
    )
    num_agreed: int = field(
        default=SFC.NOPRED,
        metadata={"msg": "Number of models that agreed on the prediction."},
    )

    def __getattr__(self, name):
        """
        Handle access to undefined attributes with proper error logging.

        This internal method intercepts attempts to access attributes that don't
        exist on the PredictionResult dataclass. It provides meaningful error
        messages and prevents AttributeError exceptions from being raised without
        context. This helps developers identify when they're trying to access
        prediction result fields that haven't been properly initialized or set.

        Args:
            name (str): The name of the attribute being accessed that doesn't exist
                on this dataclass instance.

        Returns:
            None: This method never returns normally - it always raises an
                AttributeError with a descriptive message.

        Raises:
            AttributeError: Always raised when attempting to access undefined attributes.
                        The error message includes the attribute name and indicates
                        which fields are actually available on the PredictionResult class.
        """
        logging.error(
            f"Attempted to access undefined attribute '{name}' in PredictionResult."
        )
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'. "
            "Only defined fields can be accessed."
        )
