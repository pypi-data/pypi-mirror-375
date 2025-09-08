"""Implements legacy-setup-files check."""

from pathlib import Path

from pyvelocity.checks import Check
from pyvelocity.checks import Result


class LegacySetupFiles(Check):
    """Checks that neither setup.py nor setup.cfg is used."""

    ID = "legacy-setup-files"

    def execute(self) -> Result:
        """Execute the legacy setup files check."""
        legacy_files = self._find_legacy_files()

        if not legacy_files:
            return Result(self.ID, is_ok=True, message="")

        files_list = ", ".join(legacy_files)
        message = f"Legacy setup files found: {files_list}. Use pyproject.toml instead."

        return Result(self.ID, is_ok=False, message=message)

    def _find_legacy_files(self) -> list[str]:
        """Find legacy setup files in the current directory."""
        legacy_files = []

        setup_py = Path("setup.py")
        setup_cfg = Path("setup.cfg")

        if setup_py.exists():
            legacy_files.append("setup.py")

        if setup_cfg.exists():
            legacy_files.append("setup.cfg")

        return legacy_files
