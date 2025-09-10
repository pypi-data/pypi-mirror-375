import typer
from rich import print as rprint
from rich.table import Table

from mixtrain import client as mixtrain_client

from . import dataset, secret
from .client import (
    create_dataset_provider,
    delete_dataset_provider,
    list_dataset_providers,
    update_dataset_provider,
)

app = typer.Typer(invoke_without_command=True)


@app.callback()
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def login():
    """Authenticate against the Mixtrain server. Will open a browser window for login."""
    try:
        mixtrain_client.authenticate_browser()
        rprint("[green]✓[/green] Authenticated successfully!")

        # Show new configuration
        show_config()

    except Exception as e:
        rprint(f"[red]Login failed:[/red] {str(e)}")
        rprint("Your previous authentication and workspace settings remain unchanged.")
        raise typer.Exit(1)


workspace_app = typer.Typer(
    help="Manage workspaces and configure providers", invoke_without_command=True
)


@workspace_app.callback()
def workspace_main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@workspace_app.command(name="status")
def status():
    """List available and configured dataset and model providers."""
    try:
        data = list_dataset_providers()

        # Show available dataset providers
        available = data.get("available_providers", [])
        if available:
            rprint("[bold]Available Dataset Providers:[/bold]")
            table = Table("Provider Type", "Display Name", "Description", "Status")
            for provider in available:
                table.add_row(
                    provider.get("provider_type", ""),
                    provider.get("display_name", ""),
                    provider.get("description", "")[:50] + "..."
                    if len(provider.get("description", "")) > 50
                    else provider.get("description", ""),
                    provider.get("status", ""),
                )
            rprint(table)
            rprint()

        # Show onboarded dataset providers
        onboarded = data.get("onboarded_providers", [])
        if onboarded:
            rprint("[bold]Configured Dataset and Model Providers:[/bold]")
            table = Table("ID", "Provider Type", "Display Name", "Created At")
            for provider in onboarded:
                table.add_row(
                    str(provider.get("id", "")),
                    provider.get("provider_type", ""),
                    provider.get("display_name", ""),
                    provider.get("created_at", ""),
                )
            rprint(table)
        else:
            rprint("[yellow]No dataset and model providers configured yet.[/yellow]")
            rprint("Use 'mixtrain workspace add-provider <type>' to add one.")

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

def get_provider_config_by_id(provider_id: int):
    data = list_dataset_providers()
    onboarded = data.get("onboarded_providers", [])
    provider = None
    for provider in onboarded:
        if provider.get("id") == provider_id:
            provider = provider
            break
    if not provider:
        rprint(f"[red]Error:[/red] Provider with ID {provider_id} not found.")
        raise typer.Exit(1)
    return provider

def get_provider_config(provider_type: str, ):
    # Get available dataset providers to show requirements
    data = list_dataset_providers()
    available = data.get("available_providers", [])

    # Find provider config
    provider_config = None
    for provider in available:
        if provider.get("provider_type") == provider_type:
            provider_config = provider
            break

    if not provider_config:
        rprint(f"[red]Error:[/red] Provider type '{provider_type}' not found.")
        rprint("Available dataset providers:")
        for provider in available:
            rprint(
                f"  - {provider.get('provider_type')}: {provider.get('display_name')}"
            )
        raise typer.Exit(1)

    return provider_config


@workspace_app.command(name="add-dataset-provider")
def workspace_add_dataset_provider(provider_type: str):
    """Add a new dataset provider to workspace."""
    try:
        provider_config = get_provider_config(provider_type)
        # Show dataset provider info
        rprint(f"[bold]Adding {provider_config.get('display_name')}[/bold]")
        rprint(f"Description: {provider_config.get('description', '')}")
        if provider_config.get("onboarding_instructions"):
            rprint(f"Instructions: {provider_config.get('onboarding_instructions')}")
        rprint()

        # Collect secrets
        secrets = {}
        secret_requirements = provider_config.get("secret_requirements", [])

        for req in secret_requirements:
            prompt_text = f"{req.get('display_name')} ({req.get('description')})"
            if req.get("is_required"):
                prompt_text += " [required]"
            else:
                prompt_text += " [optional]"

            # Use hidden input for sensitive data
            if any(
                keyword in req.get("name", "").lower()
                for keyword in ["key", "secret", "password", "token"]
            ):
                value = typer.prompt(prompt_text, hide_input=True)
            else:
                value = typer.prompt(
                    prompt_text, default="" if not req.get("is_required") else None
                )

            if value:
                secrets[req.get("name")] = value

        if not secrets:
            rprint("[yellow]No secrets provided. Cancelling setup.[/yellow]")
            raise typer.Exit(1)

        # Create the provider
        result = create_dataset_provider(provider_type, secrets)
        rprint(f"[green]✓[/green] Successfully added {result.get('display_name')}!")

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@workspace_app.command(name="update-dataset-provider")
def workspace_update_dataset_provider(provider_id: int):
    """Update secrets for an existing dataset provider."""
    try:
        provider = get_provider_config_by_id(provider_id)
        
        rprint(f"[bold]Updating {provider.get('display_name')}[/bold]")
        rprint()

        # Collect updated secrets
        secrets = {}
        secret_requirements = provider.get("secret_requirements", [])

        for req in secret_requirements:
            prompt_text = f"{req.get('display_name')} ({req.get('description')}) [leave empty to keep current]"

            # Use hidden input for sensitive data
            if any(
                keyword in req.get("name", "").lower()
                for keyword in ["key", "secret", "password", "token"]
            ):
                value = typer.prompt(prompt_text, default="", hide_input=True)
            else:
                value = typer.prompt(prompt_text, default="")

            # Only include non-empty values
            if value:
                secrets[req.get("name")] = value

        if not secrets:
            rprint("[yellow]No secrets updated.[/yellow]")
            return

        # Update provider
        result = update_dataset_provider(provider_id, secrets)
        rprint(f"[green]✓[/green] Successfully updated {result.get('display_name')}!")

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@workspace_app.command(name="remove-dataset-provider")
def workspace_remove_provider(provider_id: int):
    """Remove a dataset provider from workspace."""
    try:
        # Get current dataset providers
        provider = get_provider_config_by_id(provider_id)

        provider_name = provider.get("display_name")
        confirm = typer.confirm(
            f"Remove {provider_name}? This will delete all associated secrets."
        )
        if not confirm:
            rprint("Removal cancelled.")
            return

        # Remove provider
        delete_dataset_provider(provider_id)
        rprint(f"[green]✓[/green] Successfully removed {provider_name}!")

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@workspace_app.command(name="info-dataset-provider")
def workspace_info_dataset_provider(provider_type: str):
    """Show detailed information about a dataset provider."""
    try:
        data = list_dataset_providers()

        # Look in available and onboarded dataset providers
        provider_config = None
        for provider in data.get("available_providers", []):
            if provider.get("provider_type") == provider_type:
                provider_config = provider
                break

        if not provider_config:
            for provider in data.get("onboarded_providers", []):
                if provider.get("provider_type") == provider_type:
                    provider_config = provider
                    break

        if not provider_config:
            rprint(f"[red]Error:[/red] Provider type '{provider_type}' not found.")
            raise typer.Exit(1)

        # Display provider information
        rprint(f"[bold]{provider_config.get('display_name')}[/bold]")
        rprint(f"Type: {provider_config.get('provider_type')}")
        rprint(f"Status: {provider_config.get('status', 'available')}")
        rprint(f"Description: {provider_config.get('description', '')}")
        if provider_config.get("website_url"):
            rprint(f"Website: {provider_config.get('website_url')}")
        rprint()

        # Show secret requirements
        secret_requirements = provider_config.get("secret_requirements", [])
        if secret_requirements:
            rprint("[bold]Required Configuration:[/bold]")
            table = Table("Setting", "Description", "Required")
            for req in secret_requirements:
                table.add_row(
                    req.get("display_name", ""),
                    req.get("description", ""),
                    "Yes" if req.get("is_required") else "No",
                )
            rprint(table)

        # Show onboarding instructions
        if provider_config.get("onboarding_instructions"):
            rprint("\n[bold]Setup Instructions:[/bold]")
            rprint(provider_config.get("onboarding_instructions"))

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def config(
    workspace: str = typer.Option(
        None, "--workspace", "-w", help="Set the current workspace"
    ),
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
):
    """Show or modify CLI configuration."""
    if workspace:
        try:
            mixtrain_client.set_workspace(workspace)
            rprint(f"Switched to workspace: [bold]{workspace}[/bold]")
            rprint("\nUpdated configuration:")
            show_config()
        except Exception as e:
            rprint(f"[red]Error:[/red] {str(e)}")
            raise typer.Exit(1)
    else:
        show_config()


def show_config():
    """Show current configuration in a table format"""
    config = mixtrain_client.get_config()

    if not config.workspaces:
        rprint(
            "[yellow]No workspaces configured. Please run 'mixtrain login' first.[/yellow]"
        )
        return

    # Create workspaces table
    table = Table()
    table.add_column("Workspace", style="cyan")
    table.add_column("Status", style="green")

    for workspace in config.workspaces:
        status = "[green]✓ Current[/green]" if workspace.active else ""
        table.add_row(workspace.name, status)

    rprint(table)


app.add_typer(dataset.app, name="dataset")
app.add_typer(workspace_app, name="workspace")
app.add_typer(secret.app, name="secret")
# app.add_typer(train.app, name="train")
# app.add_typer(eval.app, name="eval")


def main():
    app()


if __name__ == "__main__":
    main()
