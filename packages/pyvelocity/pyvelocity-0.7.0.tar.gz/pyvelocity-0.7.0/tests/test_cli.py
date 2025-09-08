"""Tests for `pyvelocity` package."""

# Reason: Accept risk of using subprocess.
from pathlib import Path
from subprocess import run  # nosec B404
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from pyvelocity import cli
from pyvelocity.checks import Result
from pyvelocity.checks.aggregation import Results


def test_echo_success() -> None:
    cli.echo_success()


def test_echo_success_in_subprocess(temp_setup_py: Path) -> None:
    """Function echo_success() should fallback to no emoji.

    When echo emoji in subprocess on Windows, Following error raised:
      UnicodeEncodeError: 'charmap' codec can't encode characters in position 21-22
    Pyvelocity may be used in CI and it may be used in subprocess.
    see:
    - UnicodeEncodeError on Windows when there are Unicode chars in the help message
       · Issue #2121 · pallets/click
      https://github.com/pallets/click/issues/2121
    - UnicodeEncodeError in Windows agent CI pipelines
      https://gist.github.com/NodeJSmith/e7e37f2d3f162456869f015f842bcf15
    """
    # Ensure setup.py exists for legacy files check
    assert temp_setup_py.exists()

    # Reason: Accept risk of using subprocess.
    completed_process = run(  # nosec B603 B607
        "pyvelocity",  # noqa: S607
        check=False,  # Don't check return code since legacy files cause exit code 3
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    # The project has setup.py, so legacy files check will return exit code 3
    expected_exit_code_with_legacy_files = 3
    assert completed_process.returncode == expected_exit_code_with_legacy_files
    assert "Legacy setup files found: setup.py" in completed_process.stdout


@pytest.mark.parametrize(
    ("files", "expect_exit_code", "expect_message"),
    [
        (
            ["pyproject_success.toml", "setup_success.cfg"],
            3,
            "Legacy setup files found: setup.cfg. Use pyproject.toml instead.\n"
            "Error: Looks there are some of improvements.\n",
        ),
        (
            ["pyproject_error.toml", "setup_error.cfg"],
            3,
            (
                "Legacy setup files found: setup.cfg. Use pyproject.toml instead.\n"
                "Line length are not consistent.\n"
                "\tMost common = 119\n"
                "\tpyproject.toml tool.docformatter wrap-summaries = 118\n"
                "\tFlake8 tool default max-line-length = 79 (B950 in flake8-bugbear detects: 87)\n"
                "\tpyproject.toml tool.ruff line-length = 118\n"
                "Python version classifiers don't match requires-python '>=3.5': missing classifiers: "
                "Programming Language :: Python :: 3.10, "
                "Programming Language :: Python :: 3.11, "
                "Programming Language :: Python :: 3.12, "
                "Programming Language :: Python :: 3.13\n"
                "Error: Looks there are some of improvements.\n"
            ),
        ),
    ],
)
def test_command_line_interface(configured_cli_runner: CliRunner, expect_exit_code: int, expect_message: str) -> None:
    """Test the CLI."""
    result = configured_cli_runner.invoke(cli.main)
    assert result.exit_code == expect_exit_code
    assert result.output == expect_message


def test_cli_success_path(successful_result: Result) -> None:
    """Test the CLI success path to cover echo_success call."""
    # Mock all checks to return successful results
    successful_results = Results([successful_result])

    with (
        patch("pyvelocity.cli.Results", return_value=successful_results),
        patch("pyvelocity.cli.echo_success") as mock_echo_success,
    ):
        runner = CliRunner()
        result = runner.invoke(cli.main)

        assert result.exit_code == 0
        mock_echo_success.assert_called_once()


def test_help() -> None:
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
