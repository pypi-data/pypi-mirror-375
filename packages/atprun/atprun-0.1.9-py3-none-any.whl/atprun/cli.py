# https://typer.tiangolo.com/tutorial/package/

from pprint import pprint

import typer

from .app_main import AtpRunMain

app: typer.Typer = typer.Typer()
atp_run: AtpRunMain = AtpRunMain()


@app.callback()
def callback(
    config_path: str | None = typer.Option(
        default=None,
        help="Configuration file path",
    ),
):
    """
    AtpRun
    """
    # load config file
    atp_run.load_configuration(path=config_path)
    pass


@app.command()
def script(
    name: str,
):
    """
    Run script
    """
    try:
        atp_run.script_run(name=name)
    except ValueError as err:
        typer.secho(
            f"Error: {err}",
            err=True,
            fg=typer.colors.RED,
        )
    except Exception as err:
        typer.secho(
            f"Error [Unexpected]: {err}",
            err=True,
            fg=typer.colors.RED,
        )


if __name__ == "__main__":
    app()
