"""
StrainFish helper class to return prediction probabilities.

Kranti Konganti
(C) HFP, FDA.
"""

import numpy as np

from .constants import SFConstants as SFC
from .logging_utils import log


class SFProbs:
    """
    Helper class to calculate and return prediction averages over multiple
    Machine Learning algorithms.
    """

    @staticmethod
    def get_avg_probs(
        probs: np.ndarray,
        *,
        threshold: float = 0.97,
        min_percent: float = 0.95,
        dtype: np.dtype = np.float64,
    ) -> dict:
        """
        Compute per-class statistics only for columns that contain at least
        one probability >= `threshold`.

        Args:
            probs : np.ndarray, shape (n_samples, n_classes)
                Raw probability matrix. Must be 2D and contain values in
                [0, 1]. (If you already know the values are in that range you
                can skip the explicit check the function still verifies it.)

            threshold : float, default 0.97
                Minimum probability that a column must reach in order to be kept.
                Must lie in `[0, 1]`.

            min_percent : float, default 0.5
                Fraction of the column (expressed as a number between 0 and 1) that
                must contain values >= `threshold` for the column to be kept.
                For example `0.2` keeps columns where at least 20% of the rows
                exceed the threshold.

            dtype : np.dtype, default float64
                Cast the input to this type before any arithmetic is performed
                (keeps the routine numerically safe).

        Returns:
            stats : dict
                ``{
                    'average': ,
                    'count': int,
                    'k_indices': int
                }``

                *If no column survives the filter* the arrays are empty
                (`shape == (0,)`).
        """
        # ------------------------------------------------------------------
        # 1. Basic validation
        # ------------------------------------------------------------------
        if not 0.0 <= threshold <= 1.0:
            log.error(
                (
                    "Threshold must be between 0 and 1! "
                    f"Got: [bold cyan]{threshold}[/bold cyan]"
                )
            )
            raise ValueError()
        if not 0.0 <= min_percent <= 1.0:
            log.error(
                f"min_percent must be between 0 and 1! "
                f"Got: [bold cyan]{min_percent}[/bold cyan]"
            )
            raise ValueError()

        probs = np.asarray(probs, dtype=dtype)
        # print(probs)

        if probs.ndim != 2:
            log.error(
                (
                    "Probabilities must be a 2D array! Got array of shape: "
                    f"[bold cyan]{probs.shape}[/bold cyan]"
                )
            )
            raise ValueError()

        if probs.size == 0:
            # return {
            #     PRAVG: np.array([], dtype=dtype),
            #     PRCNT: np.array([], dtype=np.int64),
            #     PRKIDX: np.array([], dtype=np.int64),
            # }
            return {
                SFC.PRAVG: np.array([], dtype=dtype),
                SFC.PRCNT: np.array([], dtype=np.int64),
                SFC.PRKIDX: [],
            }

        if not np.all((probs >= 0) & (probs <= 1)):
            log.error("All probabilities must be between 0 and 1!")
            raise ValueError()

        # ------------------------------------------------------------------
        # 2. Identify columns that should be kept
        # ------------------------------------------------------------------
        # frac_vals = (probs >= threshold).mean(axis=0)
        # keep_cols = frac_vals >= min_percent
        frac_above = (probs >= threshold).any(axis=0)
        keep_cols = frac_above.mean()

        # if not keep_cols.any():
        if keep_cols < min_percent:
            # All columns were below the threshold – nothing to return
            # return {
            #     PRAVG: np.array([], dtype=dtype),
            #     PRCNT: np.array([], dtype=np.int64),
            #     PRKIDX: np.array([], dtype=np.int64),
            # }
            return {
                SFC.PRAVG: np.array([], dtype=dtype),
                SFC.PRCNT: np.array([], dtype=np.int64),
                SFC.PRKIDX: [],
            }
        # ------------------------------------------------------------------
        # 3. Work only on the retained columns
        # ------------------------------------------------------------------
        # kept = probs[:, keep_cols]
        kept = probs[:, frac_above]
        avg_per_class = kept.mean(axis=0)
        count = np.count_nonzero(kept >= threshold, axis=0)
        top_hit_idx = int(avg_per_class.argmax())

        # ------------------------------------------------------------------
        # 4. Return top hit details as a dict
        # ------------------------------------------------------------------
        return {
            SFC.PRAVG: avg_per_class[top_hit_idx],
            SFC.PRCNT: count[top_hit_idx],
            SFC.PRKIDX: [top_hit_idx],
            # PRKIDX: np.nonzero(keep_cols)[0],
        }
