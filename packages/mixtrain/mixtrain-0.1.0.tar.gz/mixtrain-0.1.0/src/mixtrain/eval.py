
import typer

from .client import call_api

app = typer.Typer(help="Manage evaluation jobs.", invoke_without_command=True)

@app.callback()
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def run(dataset_name: str, eval_func: str, dataset_version: str | None = None, limit: int | None = -1):
    """
    Start an evaluation job.
    """
    # call_api("POST", "/eval/start")
    print("Starting evaluation...")


@app.command()
def status():
    """
    Get evaluation status.
    """
    call_api("GET", "/eval/status")
