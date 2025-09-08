"""Implements aggregation of configuration files."""

from pathlib import Path

from pyvelocity.configurations.files.py_project_toml import WHERE_PY_PROJECT_TOML
from pyvelocity.configurations.files.py_project_toml import PyProjectToml


# Reason: Aggregation class. pylint: disable=too-few-public-methods
class ConfigurationFiles:
    def __init__(self) -> None:
        path_py_project_toml = Path(WHERE_PY_PROJECT_TOML)
        self.py_project_toml = PyProjectToml(path_py_project_toml) if path_py_project_toml.exists() else None
