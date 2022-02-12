"""Pre gen hooks."""

import re
import sys

MODULE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"


def main(name: str) -> None:
    """Main entrypoint of pre gen hook."""
    if not re.match(MODULE_REGEX, name):
        print(
            f"ERROR: The pkg name ({name}) is not a valid Python module name. "
            "Please do not use a - and use _ instead"
        )

        # Exit to cancel project
        sys.exit(1)


if __name__ == "__main__":
    main("{{ cookiecutter.pkg_name}}")
