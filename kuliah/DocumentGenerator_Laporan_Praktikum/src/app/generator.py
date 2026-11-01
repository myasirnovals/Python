"""Backward-compatibility shim for CLI report generator.

All CLI components now reside in `app.cli`.
"""

from .cli.generator import LegacyCliGenerator, main, render_report

__all__ = ["LegacyCliGenerator", "main", "render_report"]

if __name__ == "__main__":
    main()
