"""
StrainFish logging utilities.

Kranti Konganti
(C) HFP, FDA.
"""

import inspect
import logging
import warnings

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

from .constants import SFConstants as SFC

# Setup global logger
console = Console()
prog_name = inspect.stack()[0].filename
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(
            console=console, rich_tracebacks=True, markup=True, tracebacks_extra_lines=5
        )
    ],
)
logging.captureWarnings(True)
warnings.filterwarnings(
    action="ignore",
    message="No NVIDIA GPU detected",
    category=UserWarning,
    module=".*gpu",
)
log = logging.getLogger(prog_name)

# Setup global progress bar
progress = Progress(
    TextColumn(SFC.ISPACE),
    SpinnerColumn(),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    TextColumn("[progress.description]{task.description}"),
    TextColumn("{task.fields[info]}"),
    console=console,
    transient=True,
)

__all__ = ["log", "progress", "console"]
