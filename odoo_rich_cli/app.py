from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from odoo_rich_cli.commands import install_module, upgrade_module, uninstall_module
from odoo_rich_cli.config import resolve_config

app = typer.Typer(
    name="odoo-cli",
    help="A beautiful CLI for common Odoo module operations.",
    no_args_is_help=False,
)
console = Console()


def _run_command(
    label,        # type: str
    action_fn,
    module,       # type: str
    config_path,  # type: Optional[str]
    database,     # type: Optional[str]
):
    # type: (...) -> None
    try:
        cfg = resolve_config(config_path, database)
    except (FileNotFoundError, ValueError) as e:
        console.print(Panel(f"[red]{e}[/]", title="[bold red]Error[/]", border_style="red"))
        raise typer.Exit(1)

    with console.status(
        f"  [bold cyan]{label}[/] [yellow]{module}[/] on [bold]{cfg.db_name}[/]...",
        spinner="dots",
    ):
        result = action_fn(cfg, module)

    if result.success:
        console.print(Panel(
            f"[green]{result.message}[/]",
            title="[bold green]Success[/]",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red]{result.message}[/]",
            title="[bold red]Failed[/]",
            border_style="red",
        ))
        raise typer.Exit(1)


@app.command()
def install(
    module: str = typer.Option(..., "--module", "-m", help="Technical name of the Odoo module."),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to odoo.conf (default: ./odoo.conf)."),
    database: Optional[str] = typer.Option(None, "--database", "-d", help="Database name (overrides odoo.conf)."),
) -> None:
    """Install an Odoo module."""
    _run_command("Installing", install_module, module, config, database)


@app.command()
def upgrade(
    module: str = typer.Option(..., "--module", "-m", help="Technical name of the Odoo module."),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to odoo.conf (default: ./odoo.conf)."),
    database: Optional[str] = typer.Option(None, "--database", "-d", help="Database name (overrides odoo.conf)."),
) -> None:
    """Upgrade an Odoo module."""
    _run_command("Upgrading", upgrade_module, module, config, database)


@app.command()
def uninstall(
    module: str = typer.Option(..., "--module", "-m", help="Technical name of the Odoo module."),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to odoo.conf (default: ./odoo.conf)."),
    database: Optional[str] = typer.Option(None, "--database", "-d", help="Database name (overrides odoo.conf)."),
) -> None:
    """Uninstall an Odoo module."""
    _run_command("Uninstalling", uninstall_module, module, config, database)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to odoo.conf (default: ./odoo.conf)."),
    database: Optional[str] = typer.Option(None, "--database", "-d", help="Database name (overrides odoo.conf)."),
) -> None:
    """Launch the interactive menu if no command is given."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["database"] = database
    if ctx.invoked_subcommand is None:
        from odoo_rich_cli.menu import interactive_menu

        interactive_menu(config, database)
