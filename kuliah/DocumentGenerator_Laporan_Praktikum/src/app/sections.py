"""Backward-compatibility shim for CLI section collector.

All CLI components now reside in `app.cli`.
"""

from .cli.sections import ReportSectionsCollector

__all__ = ["ReportSectionsCollector"]
