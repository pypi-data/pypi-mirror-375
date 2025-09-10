"""
StrainFish SentencePiece configuration definitions.

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
class SentencePieceConfig:
    """Configuration class for SentencePiece encoding.

    Override any of them on the CLI with the
    --sp- prefix (e.g. --sp-max-depth 15).
    """

    # --------------------------------------------------------
    # 1. General parameters.
    # --------------------------------------------------------
    max_piece_length: int = field(
        default=20,
        metadata=_h("Maximum length of sentence pieces."),
    )
    normalize_rule: str = field(
        default="identity",
        metadata=_h("Normalization rule to apply."),
    )
    max_sentence_length: int = field(
        default=8000,
        metadata=_h(
            "Specifies the maximum length of an input sentence, measured in bytes. "
            "During training, sentences exceeding this length are simply ignored, "
            "helping prevent issues like overflow during Unigram model training "
            " and performance degradation with BPE."
        ),
    )
    vocab_size: int = field(
        default=1024,
        metadata=_h("Size of vocabulary for input DNA corpus."),
    )
    enc_type: str = field(
        default="bpe",
        metadata=_h(
            "Type of SentencePiece encoding. Valid options are 'bpe' or 'char'."
        ),
    )
    hard_vocab_limit: bool = field(
        default=False,
        metadata=_h("Whether to enforce strict vocabulary limit."),
    )
    char_cov: float = field(
        default=1.0,
        metadata=_h(
            "Character coverage expressed as percetage fraction, i.e., 0 to 1."
        ),
    )

    # --------------------------------------------------------
    # 2. Return config parameters.
    # --------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Return a nested dictionary suitable for `SentencePiece`.
        The outer key 'sp' mirrors the CLI prefix.
        """
        return {"sp": {f.name: getattr(self, f.name) for f in fields(self)}}
