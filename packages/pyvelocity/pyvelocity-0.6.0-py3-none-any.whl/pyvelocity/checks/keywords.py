"""Implements keywords check."""

from pyvelocity.checks import Check
from pyvelocity.checks import Result
from pyvelocity.configurations.files.sections.project import Project


class Keywords(Check):
    """Checks that at least one keyword is defined in the project section."""

    ID = "keywords"

    def execute(self) -> Result:
        if self.configuration_files.py_project_toml is None:
            return Result(self.ID, is_ok=False, message="pyproject.toml is required for keywords check")

        if self.configuration_files.py_project_toml.project is None:
            return Result(self.ID, is_ok=False, message="Project section is missing in pyproject.toml")

        return self.check_keywords(self.configuration_files.py_project_toml.project)

    def check_keywords(self, project: Project) -> Result:
        """Checks that at least one keyword is defined in the project section."""
        keywords_value = project.keywords.value

        if keywords_value is None:
            return Result(
                self.ID,
                is_ok=False,
                message="keywords field is missing in [project] section of pyproject.toml",
            )

        if not isinstance(keywords_value, list):
            return Result(
                self.ID,
                is_ok=False,
                message="keywords field must be a list in [project] section of pyproject.toml",
            )

        if len(keywords_value) == 0:
            return Result(
                self.ID,
                is_ok=False,
                message="At least one keyword must be defined in [project] section of pyproject.toml",
            )

        return Result(self.ID, is_ok=True, message="")
