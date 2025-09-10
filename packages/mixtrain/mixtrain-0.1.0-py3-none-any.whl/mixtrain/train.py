from enum import Enum

import modal
import typer

from .client import call_api

app = typer.Typer(help="Manage training jobs.", invoke_without_command=True)

@app.callback()
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def start():
    """
    Start a training job.
    """
    call_api("POST", "/training/start")


@app.command()
def status():
    """
    Get training status.
    """
    call_api("GET", "/training/status")

class Framework(str, Enum):
    oxen = "oxen"
    pytorch = "pytorch"
    tensorflow = "tensorflow"
    axolotl = "axolotl"

@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def run(ctx: typer.Context,
        path: str = typer.Option(".", help="The path to the training data."),
        gpu: str = typer.Option("T4", help="The GPU to use."),
        framework: Framework = typer.Option(None, help="The framework to use."),
        extra_libs: list[str] = typer.Option([], help="Extra libraries to install."),
        ):
    """
    Run a training job.
    """
    print(f"Using GPU: {gpu}")
    for arg in ctx.args:
        typer.echo(f"- {arg}")


    app = modal.App.lookup("train-app",create_if_missing=True)
    if framework == Framework.axolotl:

        image = modal.Image.from_registry("axolotlai/axolotl-cloud:main-20250701-py3.11-cu124-2.6.0").pip_install(extra_libs).env({
            "JUPYTER_DISABLE": "1",
        })

    with modal.enable_output():
        sandbox = modal.Sandbox.create(image=image, gpu=gpu, app=app, timeout=600, verbose=True) # you can pass cmd here as well
        print(sandbox.object_id)
        p = sandbox.exec("python", "-c", "import torch; print(torch.cuda.get_device_name())")
        for line in p.stdout:
            print(line, end="")
        # print(p.stdout.read())
        # print(p.stderr.read())

        p = sandbox.exec("python", "-c", "import duckdb; print(duckdb.__version__)")
        # for line in p.stdout:
        #     print(line, end="")
        print(p.stdout.read())
        print(p.stderr.read())

        sandbox.terminate()
