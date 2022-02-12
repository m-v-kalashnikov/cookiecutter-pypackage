"""Console script for {{cookiecutter.pkg_name}}."""

{% if cookiecutter.command_line_interface|lower == 'y' -%}
import typer

main = typer.Typer()


@main.command()
def run() -> None:
    """Main entrypoint."""
    typer.secho("{{ cookiecutter.project_slug }}", fg=typer.colors.BRIGHT_WHITE)
    typer.secho("=" * len("{{ cookiecutter.project_slug }}"), fg=typer.colors.BRIGHT_WHITE)
    typer.secho(
        "{{ cookiecutter.project_short_description }}",
        fg=typer.colors.BRIGHT_WHITE,
    )


if __name__ == "__main__":
    main()  # pragma: no cover
{%- endif %}
