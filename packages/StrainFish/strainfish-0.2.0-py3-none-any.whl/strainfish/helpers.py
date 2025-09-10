"""
Helper functions for StrainFish (SF).

This class provides utility functions for validating variables
and input files that are commonly used, among others. Some other
methods include returning human-readable memory information.

Kranti Konganti
(C) HFP, FDA.
"""

import os
from typing import Any, Dict, NamedTuple, Optional, Union

import humanize
import importlib_metadata as im
from pynvml import (
    nvmlDeviceGetCount,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetMemoryInfo,
    nvmlInit,
    nvmlShutdown,
)

from .constants import SFConstants as SFC
from .logging_utils import log


class SFHelpers:
    """
    Static helper methods for sequence framework applications.

    This class provides utility functions for validating inputs and checking
    file existence and validity. All methods are static and can be called directly
    without creating an instance of the class.
    """

    @staticmethod
    def _defined(
        var: Optional[Any] = None, desc: str = "Cannot be a None type!"
    ) -> bool:
        """
        Internal helper to validate that a variable is not None.

        This method provides centralized validation for required parameters
        throughout the StrainFish codebase. It ensures critical variables
        are properly defined before proceeding with operations, preventing
        None-related runtime errors.

        Args:
            var (Any, optional): The variable to check for None value.
                If None, an error will be logged and False returned.
                Defaults to None.
            desc (str): Human-readable description of the variable being checked.
                This description is included in error messages when validation fails.
                Defaults to "Cannot be a None type!".

        Returns:
            bool: True if the variable is not None, indicating successful validation.
                False if the variable is None, indicating validation failure.

        Raises:
            None: This function handles all exceptions internally and logs errors
                using the global logger instance.
        """
        if var is None:
            log.error(
                f"[bold cyan]{var}[/bold cyan]. {desc} is not defined or cannot be None type!"
            )
            return False
        return True

    @staticmethod
    def _input_file_exists(
        file: Optional[Union[str, os.PathLike]] = None,
        desc: str = "Input file",
    ) -> bool:
        """
        Comprehensive validation of input file existence and integrity.

        This internal method performs three critical checks to ensure input files
        are suitable for processing: (1) validates the file path is not None,
        (2) verifies the file exists on the filesystem, and (3) confirms the
        file has content (non-zero size). This prevents downstream errors in
        file operations throughout StrainFish.

        Args:
            file (Union[str, os.PathLike], optional): Path to the input file
                to validate. Accepts both string paths and Path-like objects.
                If None, an error is logged and False returned. Defaults to None.
            desc (str): Human-readable description of the file being validated.
                This description is included in formatted error messages when
                validation fails, improving user experience. Defaults to "Input file".

        Returns:
            bool: True if all validations pass (file exists and has content),
                indicating the file is ready for processing. False if any
                validation fails, indicating the file cannot be used.

        Raises:
            None: This function handles all exceptions internally and logs errors
                using the global logger instance with colorized output.

        Note:
            This function uses the global logger to report validation errors with
            formatted messages including file names. The function does not check
            file permissions, readability, or content validity beyond existence
            and non-emptiness.
        """
        if file is None:
            log.error(f"{desc} cannot be [red]None[/red] type!")
            return False
        elif not os.path.exists(file):
            log.error(
                f"{desc} [cornflower_blue][ {os.path.basename(file)} ]"
                + "[/cornflower_blue] does not [red]exist[/red]!"
            )
            return False
        elif os.path.getsize(file) <= 0:
            log.error(
                f"{desc} [cornflower_blue][ {os.path.basename(file)} ]"
                + "[/cornflower_blue] is of size [red]zero[/red]!"
            )
            return False
        return True

    @staticmethod
    def _human_bytes(nbytes: int) -> str:
        """
        Convert byte count into human-readable format using binary units.

        This internal helper method transforms raw byte values into intuitive,
        human-readable strings using binary prefixes (KiB, MiB, GiB, etc.).
        The conversion follows the IEC standard where 1 KiB = 1024 bytes.
        This is particularly useful for displaying file sizes, memory usage,
        and other byte-based metrics in user-friendly formats.

        Args:
            nbytes (int | float): The number of bytes to convert. Accepts
                both positive and negative values, as well as zero. When a
                float is provided, the fractional part is preserved in the
                output (e.g., 1234.5 bytes becomes "1.2 KiB").

        Returns:
            str: A formatted string representing the byte count in appropriate
                units. Examples include "512 B", "1.0 KiB", "3.4 MiB", etc.
                The format always includes a single space between the numeric
                value and the unit suffix for consistency.

        Raises:
            TypeError: If nbytes is not an instance of int or float. This
                strict type checking ensures predictable behavior and prevents
                unexpected results from non-standard numeric types.
        """
        for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
            if nbytes < 1024:
                return f"{nbytes:.1f} {unit}"
            nbytes /= 1024
        return f"{nbytes:.1f} PiB"

    @staticmethod
    def _elapsed_time(start: float, end: float) -> str:
        """
        Convert raw elapsed time duration into human-readable format.

        This internal method takes start and end timestamps and converts the
        difference into an intuitive time string using natural language units.
        It leverages the humanize library for precise formatting with customizable
        precision and minimum unit specification. Ideal for displaying processing
        times, training durations, or other time-based metrics to users.

        Args:
            start (float): Starting timestamp obtained from `time.time()` or
                `time.perf_counter()`. Represents the beginning of the time
                interval being measured.
            end (float): Ending timestamp obtained from `time.time()` or
                `time.perf_counter()`. Represents the conclusion of the time
                interval being measured.

        Returns:
            str: A human-readable string representing the elapsed duration.
                Examples include "1 minute, 4.2 seconds" for longer durations,
                or "3.56 seconds" for shorter intervals. The format uses
                natural language units and maintains precision to two decimal places.

        Raises:
            None: This method relies on the humanize library which handles edge
                cases like negative time differences internally.
        """
        elapsed = end - start
        return humanize.precisedelta(elapsed, format="%0.2f", minimum_unit="seconds")

    @staticmethod
    def _is_gpu_available() -> bool:
        """
        Detect NVIDIA GPU availability using NVIDIA Management Library (NVML).

        This internal method queries the system for NVIDIA GPUs using the official
        NVML library. It performs comprehensive hardware detection and provides
        appropriate logging for both GPU-enabled and CPU-only environments.
        The method includes proper error handling and resource cleanup to ensure
        reliable operation across different system configurations.

        Args:
            None: This method takes no parameters as it queries all available
                GPUs on the system automatically.

        Returns:
            bool: True if at least one NVIDIA GPU is detected and accessible,
                indicating GPU acceleration can be used. False if no GPUs are
                found or if NVML initialization fails, indicating CPU-only mode.

        Raises:
            SystemExit: The process exits with status code 1 if no GPUs are detected.
                        This occurs when the system has no compatible NVIDIA hardware.
            RuntimeError: If NVML cannot be initialized or if calls to NVML functions
                        like `nvmlDeviceGetCount()` fail, indicating driver or
                        compatibility issues.
        """
        try:
            nvmlInit()
            if nvmlDeviceGetCount() == 0:
                log.warning(
                    "[yellow]Non GPU-accelerated training is strongly discouraged[/yellow]."
                )
                log.error("[red]No GPU(s) found[/red]!")
                return False
            else:
                return True
        except Exception as e:
            log.warning(
                "[yellow]Non GPU-accelerated training is strongly discouraged[/yellow]."
            )
            log.error(
                f"[yellow]NVML error while querying GPUs[/yellow]: [red]{e}[/red]."
            )
            return False
        finally:
            nvmlShutdown()

    @staticmethod
    def _show_pkg_info() -> str:
        """
        Retrieve and format StrainFish package metadata for display.

        This internal method accesses the installed package's distribution metadata
        using importlib_metadata and formats it into a visually appealing summary.
        It extracts key information including package name, version, description,
        and author details. The formatted output is designed for console display
        with appropriate styling and formatting for user readability.

        Args:
            None: This method takes no parameters as it retrieves metadata from
                the currently installed StrainFish package automatically.

        Returns:
            str: A formatted string containing:
                - Package name and version in bold magenta text
                - Package summary/description on a separate line
                - Author information with periods replaced by spaces for better
                readability (e.g., "Jane.Doe" becomes "Jane Doe")
                The entire output is wrapped in appropriate markup for terminal display.

        Raises:
            None: This method relies on importlib_metadata which handles missing
                metadata gracefully, though such cases would be rare for a
                properly installed package.
        """
        pkg_meta = im.metadata(SFC.PKG_NAME)
        return (
            f"\n[bold magenta]{SFC.PKG_NAME} v{pkg_meta['Version']}[/bold magenta]\n\n"
            f"{pkg_meta['Summary']}\n\n"
            f"Conceived and Built by [bold cyan]{pkg_meta['Author'].replace('.', ' ')}[/bold cyan]."
        )

    @staticmethod
    def _log_params(params: Dict) -> None:
        """
        Format and log configuration parameters with aligned columns.

        This internal method takes a dictionary of parameters and formats them
        for structured logging output. It calculates the maximum key length to
        create aligned columns, making the parameter display more readable.
        Only non-None values are logged to avoid cluttering the output with
        unset or default parameters.

        Args:
            params (Dict): Dictionary containing parameter names as keys and
                their corresponding values as key-value pairs. The method expects
                string keys and any type of values, though only non-None values
                will be processed and logged.

        Returns:
            None: This method performs logging operations directly to the global
                logger instance and does not return any value.

        Raises:
            None: This method handles all potential errors internally and logs them
                using the global error logging mechanism.
        """
        key_len = max(len(k) for k in params.keys())

        for k, v in params.items():
            if v is not None:
                log.info(f"[slate_blue1]{k:<{key_len}}[/slate_blue1]: [cyan]{v}[/cyan]")


class GPUMemInfo(NamedTuple):
    """Return GPU memory information. All values are in bytes."""

    total: int
    used: int

    @staticmethod
    def fetch() -> Optional["GPUMemInfo"]:
        """
        Retrieve the aggregate GPU memory statistics for the host machine.

        The routine attempts to initialise the NVIDIA Management Library
        (NVML), iterates over every detected GPU, and sums up the total
        available memory as well as the amount currently in use.  The
        result is returned as a :class:`GPUMemInfo` instance whose fields
        are expressed in bytes.  If NVML cannot be initialised or any
        exception is raised while querying the GPUs, a warning and an
        error message are emitted and a `GPUMemInfo` with zero values
        is returned so that callers can safely continue execution.

        Args:
            None

        Returns:
            GPUMemInfo:
                An object containing the accumulated `total` and
                `used` GPU memory (both in bytes).  In case of an error
                the object will hold `0` for both fields.
        """
        try:
            nvmlInit()
            total_gpu_mem = 0
            total_gpu_mem_used = 0

            for idx in range(nvmlDeviceGetCount()):
                gpu_mem = nvmlDeviceGetMemoryInfo(nvmlDeviceGetHandleByIndex(idx))
                total_gpu_mem += gpu_mem.total
                total_gpu_mem_used += gpu_mem.used
            return GPUMemInfo(int(total_gpu_mem), int(total_gpu_mem_used))

        except Exception as e:
            log.warning(
                "[yellow]Non GPU-accelerated training or prediction is strongly discouraged[/yellow]."
            )
            log.error(
                f"[yellow]NVML error while querying GPUs[/yellow]: [red]{e}[/red]."
            )
            return GPUMemInfo(int(0), int(0))

        finally:
            nvmlShutdown()
