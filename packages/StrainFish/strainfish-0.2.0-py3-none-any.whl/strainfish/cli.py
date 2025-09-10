"""
StrainFish CLI interface.

Kranti Konganti
(C) HFP, FDA.
"""

import rich_click as click

from .commands.predict import predict_params
from .commands.train import train_params
from .commands.version import version_info


# ----------------------------------------------------------------------
# 1. Root command group: strainfish --help
# ----------------------------------------------------------------------
@click.group()
def strainfish() -> None:
    """
    StrainFish: An Ensemble Machine Learning algorithm for
    classification of bacterial strains.
    """
    pass


# ----------------------------------------------------------------------
# 2. Register the sub‑commands
# ----------------------------------------------------------------------
strainfish.add_command(train_params)
strainfish.add_command(predict_params)
strainfish.add_command(version_info)


# ----------------------------------------------------------------------
# 3. Entry point for strainfish
# ----------------------------------------------------------------------
if __name__ == "__main__":
    strainfish()
