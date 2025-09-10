"""
Test helper utilities for StrainFish.

This module provides utility functions and constants specifically designed
for testing StrainFish components. It includes environment management,
command execution helpers, and test-specific configurations.

Kranti Konganti
(C) HFP, FDA.
"""

from click.testing import CliRunner


class SFTestHelpers:
    """
    Static helper methods for StrainFish testing.

    This class provides utility functions specifically designed for testing
    StrainFish components. All methods are static and can be called directly
    without creating an instance of the class.
    """

    @staticmethod
    def get_cli_runner() -> CliRunner:
        """
        Helper function to provide a Click testing runner.

        Returns:
            CliRunner: A Click testing runner for invoking CLI commands programmatically.
        """
        return CliRunner()
