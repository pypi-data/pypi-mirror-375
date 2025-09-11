"""
StrainFish Global Constants.

Kranti Konganti
(C) HFP, FDA.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, List


@dataclass(frozen=True)
class StrainFishConstants:
    """
    StrainFish global constants organized into logical groups for better readability and maintainability.

    This class consolidates all global constants used throughout the StrainFish application,
    grouped by functionality to improve code organization and reduce import clutter.
    """

    # ----------------------------------------------------------------------
    # 1. Package and directory paths
    # ----------------------------------------------------------------------
    PKG_NAME: Final[str] = "StrainFish"
    PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent
    MODELS_DIR: Final[Path] = Path(PROJECT_ROOT, "models")

    # ----------------------------------------------------------------------
    # 2. Model file suffixes and prefixes
    # ----------------------------------------------------------------------
    NUM_MODELS: Final[int] = 3

    XGB_PREFIX_U: Final[str] = "xgb_"
    RF_PREFIX_U: Final[str] = "rf_"
    SP_PREFIX_U: Final[str] = "sp_"
    IMB_PREFIX_U: Final[str] = "imb_"

    XGB_PREFIX: Final[str] = "xgb"
    RF_PREFIX: Final[str] = "rf"
    SP_PREFIX: Final[str] = "sp"
    IMB_PREFIX: Final[str] = "imb"

    # Model file suffixes
    SP_CRPS_SUFFIX: Final[str] = ".sp.corpus"
    SP_C_CRPS_SUFFIX: Final[str] = ".model"
    TF_CRPS_SUFFIX: Final[str] = ".tf.corpus.jl"
    XGB_SUFFIX: Final[str] = ".xgb.ubj"
    RF_SUFFIX: Final[str] = ".rf.tl"
    NB_SUFFIX: Final[str] = ".nb.jl"
    LBL_SUFFIX: Final[str] = ".lbls.jl"

    # ----------------------------------------------------------------------
    # 3. Encoding methods and parameters
    # ----------------------------------------------------------------------
    SOMH: Final[str] = "sm"
    SPEC: Final[str] = "sp"
    TFIDF: Final[str] = "tf"

    NBR: Final[str] = "num_boost_round"
    ESR: Final[str] = "early_stopping_rounds"
    VE: Final[str] = "verbose_eval"

    IMCLSW: Final[str] = "imbal_class_weight"
    NUMC: Final[str] = "num_class"

    RFNE: Final[str] = "n_estimators"
    RFMD: Final[str] = "max_depth"
    RFRS: Final[str] = "random_state"
    RFNB: Final[str] = "n_bins"
    RFMF: Final[str] = "max_features"
    RFMSL: Final[str] = "min_samples_leaf"
    RFMSS: Final[str] = "min_samples_split"
    RFBOO: Final[str] = "bootstrap"
    RFVRB: Final[int] = "verbose"
    RFSC: Final[str] = "split_criterion"

    # Imbalance handling parameters
    IMBSENNSS: Final[str] = "smote_enn_s_s"
    IMBSENNNJ: Final[str] = "smote_enn_n_jobs"
    IMBSKN: Final[str] = "smote_k_neighbors"
    IMBSEN: Final[str] = "enn_n_neighbors"

    # SentencePiece parameters
    SPMPLKN: Final[str] = "max_piece_length"
    SPMSLKN: Final[str] = "max_sentence_length"
    SPNRKN: Final[str] = "normalize_rule"
    SPVSKN: Final[str] = "vocab_size"
    SPETKN: Final[str] = "enc_type"
    SPHVLKN: Final[str] = "hard_vocab_limit"
    SPCCKN: Final[str] = "char_cov"

    # ----------------------------------------------------------------------
    # 4. Default configuration parameters
    # ----------------------------------------------------------------------
    CHKS: Final[int] = 200
    NH: Final[int] = 100
    FC: Final[int] = 21
    DKMER: Final[int] = 7
    SPCOLS: Final[int] = 100

    CHKSN: Final[str] = "chunk_size"
    NHN: Final[str] = "n_hashes"
    FCN: Final[str] = "ov_factor"
    DKMERN: Final[str] = "kmer"
    ENCDRN: Final[str] = "encoder"
    PDLEN: Final[str] = "padding_length"
    PRTHR: Final[str] = "threshold"
    PRMIP: Final[str] = "min_percent"
    PRAVG: Final[str] = "average"
    PRKIDX: Final[str] = "k_indices"
    PRCNT: Final[str] = "count"
    PRFTHR: Final[float] = 0.2

    SMPNM: Final[str] = "sample_name"

    XGBWT: Final[str] = "xgb_weight"

    # Confidence thresholds
    VHCONF: Final[str] = "VERY HIGH"
    HCONF: Final[str] = "HIGH"
    MCONF: Final[str] = "MODERATE"
    LCONF: Final[str] = "LOW"
    MODTHR: Final[float] = 0.8
    LOWTHR: Final[float] = 0.5

    # User thresholds
    USRTHR: Final[float] = 0.0
    USRMP: Final[float] = 0.0

    ACONF: Final[str] = "Ambiguous"
    ICONF: Final[str] = "Incorrect"

    # ----------------------------------------------------------------------
    # 5. File extensions and related constants
    # ----------------------------------------------------------------------
    FASUFFIXES: Final[List[str]] = field(
        default_factory=lambda: [".fa", ".fasta", ".fna", ".fas"]
    )

    HROWS: Final[int] = 5
    TROWS: Final[int] = 5

    ISPACE: Final[str] = "          "
    NOPRED: Final[str] = "-"

    # ----------------------------------------------------------------------
    # 6. Algorithm-specific constants
    # ----------------------------------------------------------------------
    PSEKNC_W: Final[float] = 0.1
    XGBWT_V: Final[float] = 0.85


# Create a single global instance to be imported throughout the application
SFConstants = StrainFishConstants()
