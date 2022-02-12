"""
Test module for project generation
"""

import datetime
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

import pytest
from cookiecutter.utils import rmtree
from pytest_cookies.plugin import Cookies, Result

_DEPENDENCY_FILE = "pyproject.toml"
_INSTALL_DEPS_COMMANDS = [
    "poetry install",
]


@contextmanager
def in_out_dir(dir_path: Path) -> Generator[None, None, None]:
    """
    Execute code from inside the given directory and then exiting
    """

    back = Path.cwd()

    try:
        os.chdir(dir_path)
        yield
    finally:
        os.chdir(back)


@contextmanager
def bake_in_temp_dir(
    cookies: Cookies, *args: Any, **kwargs: Any
) -> Generator[Result, None, None]:
    """
    Delete the temporal directory that is created when executing the tests
    """

    result = cookies.bake(*args, **kwargs)

    try:
        yield result
    finally:
        rmtree(result.project_path)


def execute(
    command: list[str],
    dir_path: Path,
    timeout: float | None = 30,
    supress_warning: bool = True,
) -> str:
    """
    Run command inside given directory and returns output

    if there's stderr, then it may raise exception according to supress_warning
    """
    with in_out_dir(dir_path):
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process:

            stdout, stderr = process.communicate(timeout=timeout)
            out = stdout.decode("utf-8")
            err = stderr.decode("utf-8")

            if err and not supress_warning:
                raise RuntimeError(err)

            print(err)
            return out


class TestGeneration:
    """
    Test of project generation with different parameters
    """

    @staticmethod
    def get_path(to_check: Any) -> Path:
        """
        Get path or raise error in argument in not path
        """
        assert isinstance(to_check, Path)
        return to_check

    @classmethod
    def project_info(cls, result: Result) -> tuple[Path, str, Path]:
        """
        Get toplevel dir, project_slug, and project dir from baked cookies
        """

        project_path = cls.get_path(result.project_path)
        project_slug = project_path.name
        package_path = project_path / project_slug.replace("-", "_")

        return project_path, project_slug, package_path

    def test_bake_with_defaults(self, cookies: Cookies) -> None:
        """
        Test project creating with default values
        """
        with bake_in_temp_dir(cookies) as result:
            assert result.exit_code == 0
            assert result.exception is None

            project_path = self.get_path(result.project_path)
            assert project_path.is_dir()

            toplevel_files = [e.name for e in project_path.iterdir()]
            assert _DEPENDENCY_FILE in toplevel_files
            assert "python_boilerplate" in toplevel_files
            assert ".gitignore" in toplevel_files
            assert "tests" in toplevel_files

            mkdocs_yml = project_path / "mkdocs.yml"
            assert "  - Home: index.md\n" in mkdocs_yml.open().readlines()

    def test_year_compute_in_license_file(self, cookies: Cookies) -> None:
        """
        Test if year in LICENCE match to current year
        """
        with bake_in_temp_dir(cookies) as result:

            license_file = self.get_path(result.project_path) / "LICENSE"
            assert license_file.is_file()

            now = datetime.datetime.now()
            assert str(now.year) in license_file.open().read()

    def test_bake_not_open_source(self, cookies: Cookies) -> None:
        """
        Test if Licence absent when project is not open source
        """
        with bake_in_temp_dir(
            cookies, extra_context={"open_source_license": "Not open source"}
        ) as result:
            project_path = self.get_path(result.project_path)
            toplevel_files = [e.name for e in project_path.iterdir()]
            assert _DEPENDENCY_FILE in toplevel_files
            assert "LICENSE" not in toplevel_files
            assert "License" not in (project_path / "README.md").open().read()
            assert "License" not in (project_path / _DEPENDENCY_FILE).open().read()

    @pytest.mark.parametrize(
        "args",
        [
            ({"command_line_interface": "n"}, False),
            ({"command_line_interface": "y"}, True),
        ],
    )
    def test_bake_with_and_without_console_script(
        self, cookies: Cookies, args: list[tuple[dict[str, str], bool]]
    ) -> None:
        """
        Test if it creates cli.py and add parameters to files
        when it required and vise-versa
        """
        context, is_present = args
        result = cookies.bake(extra_context=context)
        project_path, project_slug, package_path = self.project_info(result)
        cli = package_path / "cli.py"
        assert cli.exists() == is_present

        pyproject_file = project_path / _DEPENDENCY_FILE
        assert ("[tool.poetry.scripts]" in pyproject_file.open().read()) == is_present

        if is_present:
            call_raw = execute(
                [sys.executable, str(cli)], dir_path=package_path, supress_warning=False
            )
            assert project_slug in call_raw

            call_help = execute(
                [sys.executable, str(cli), "--help"],
                dir_path=package_path,
                supress_warning=False,
            )
            help_lines = list(
                filter(lambda line: "--help" in line, call_help.split("\n"))
            )
            assert len(help_lines) == 1

            help_text = help_lines[0]
            assert "Show this message and exit." in help_text

    @pytest.mark.parametrize(
        "license_info",
        [
            ("MIT", "MIT "),
            (
                "BSD-3-Clause",
                "Redistributions of source code must retain the "
                + "above copyright notice, this",
            ),
            ("ISC", "ISC License"),
            ("Apache-2.0", "Licensed under the Apache License, Version 2.0"),
            ("GPL-3.0-only", "GNU GENERAL PUBLIC LICENSE"),
        ],
    )
    def test_bake_with_various_licenses(
        self, cookies: Cookies, license_info: tuple[str, str]
    ) -> None:
        """
        Test project generation with various licenses
        """
        license_type, target_string = license_info
        with bake_in_temp_dir(
            cookies, extra_context={"open_source_license": license_type}
        ) as result:
            assert (
                target_string
                in (self.get_path(result.project_path) / "LICENSE").open().read()
            )
            assert (
                license_type
                in (self.get_path(result.project_path) / _DEPENDENCY_FILE).open().read()
            )

    @pytest.mark.parametrize(
        "args",
        [
            ({"install_precommit_hooks": "n"}, False),
            ({"install_precommit_hooks": "y"}, True),
        ],
    )
    def test_bake_with_and_without_installing_precommit_hooks(
        self, cookies: Cookies, args: list[tuple[dict[str, str], bool]]
    ) -> None:
        """
        Test if it creates required files for git hooks
        when it required and vise-versa
        """
        context, is_present = args
        result = cookies.bake(extra_context=context)
        project_path = self.get_path(result.project_path)
        pre_commit = project_path / ".git/hooks/pre-commit"
        assert pre_commit.is_file() == is_present

        pyproject_file = project_path / _DEPENDENCY_FILE
        assert ("pre-commit =" in pyproject_file.open().read()) == is_present
