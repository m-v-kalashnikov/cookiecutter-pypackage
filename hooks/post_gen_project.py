"""Post gen hooks."""

import os
import shlex
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

PROJECT_DIRECTORY = Path.cwd()


@contextmanager
def inside_dir(dir_path: Path) -> Generator[None, None, None]:
    """Execute code from inside the given directory."""
    old_path = Path.cwd()

    try:
        os.chdir(dir_path)
        yield
    finally:
        os.chdir(old_path)


def run_inside_dir(commands: list[str] | tuple[str], dir_path: Path) -> None:
    """Run a commands from inside a given directory."""
    with inside_dir(dir_path):
        for command in commands:
            subprocess.check_call(shlex.split(command))


def init_git() -> None:
    """Initialize git in generated project."""
    git = PROJECT_DIRECTORY / ".git"

    if not git.is_dir():
        run_inside_dir(
            commands=[
                "git config --global init.defaultBranch main",
                "git init",
            ],
            dir_path=PROJECT_DIRECTORY,
        )


def install_pre_commit_hooks() -> None:
    """Install pre-commit."""
    run_inside_dir(
        commands=[
            f"{sys.executable} -m pip install --upgrade --no-input --quiet pip",
            f"{sys.executable} -m pip install --upgrade --no-input --quiet pre-commit",
            f"{sys.executable} -m pre_commit install",
        ],
        dir_path=PROJECT_DIRECTORY,
    )


if __name__ == "__main__":

    if "{{ cookiecutter.command_line_interface|lower }}" != "y":
        cli_file = PROJECT_DIRECTORY / "{{ cookiecutter.pkg_name }}/cli.py"
        cli_file.unlink(missing_ok=True)

    if "{{ cookiecutter.open_source_license|lower }}" == "not open source":
        license_file = PROJECT_DIRECTORY / "LICENSE"
        license_file.unlink(missing_ok=True)

    init_git()

    if "{{ cookiecutter.install_precommit_hooks|lower }}" == "y":
        install_pre_commit_hooks()
