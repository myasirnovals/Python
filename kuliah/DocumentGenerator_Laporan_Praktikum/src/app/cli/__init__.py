"""CLI package for interactive terminal report generation."""

from .generator import LegacyCliGenerator, render_report
from .input_helpers import ConsoleInput
from .sections import ReportSectionsCollector

__all__ = [
    "ConsoleInput",
    "LegacyCliGenerator",
    "ReportSectionsCollector",
    "render_report",
]

