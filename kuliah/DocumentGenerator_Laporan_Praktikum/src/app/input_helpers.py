"""Backward-compatibility shim for CLI console input.

All CLI components now reside in `app.cli`.
"""

from .cli.input_helpers import ConsoleInput

__all__ = ["ConsoleInput"]
