# Console Script Setup

Optionally, your package can include a console script using [Typer].

# How It Works

If the `command_line_interface` option is set to `y` during setup, cookiecutter
 will add a file `cli.py` in the `pkg_name` subdirectory. An entry point is added to
`pyproject.toml` that points to the main function in cli.py.

# Usage

To use the console script in development:

``` bash
poetry install
```

Then execute:
```
$project_slug --help
```

it will show your package name, project short description and exit.

# More Details

You can read more how to work with console scripts at [Typer].

[Typer]: https://typer.tiangolo.com/
