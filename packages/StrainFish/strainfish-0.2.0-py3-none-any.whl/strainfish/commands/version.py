"""
StrainFish `version` CLI interface.

Kranti Konganti
(C) HFP, FDA.
"""

import rich_click as click
from rich.panel import Panel

from ..constants import SFConstants as SFC
from ..helpers import SFHelpers
from ..logging_utils import console


@click.command(name="version")
def version_info() -> None:
    """Show package version."""
    console.print(
        Panel.fit(
            SFHelpers._show_pkg_info(),
            title=SFC.PKG_NAME,
            border_style="spring_green3",
            padding=(1, 1, 1, 1),
        )
    )
