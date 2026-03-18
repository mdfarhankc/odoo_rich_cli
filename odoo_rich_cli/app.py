from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from odoo_rich_cli.commands import (
    install_module,
    upgrade_module,
    uninstall_module,
    update_list as update_list_cmd_fn,
    module_info as module_info_cmd_fn,
    list_modules as list_modules_cmd_fn,
    clear_assets as clear_assets_cmd_fn,
    reset_password as reset_password_cmd_fn,
    shell_exec as shell_exec_cmd_fn,
)
from odoo_rich_cli.config import resolve_config

app = typer.Typer(
    name="odoo-cli",
    help="A beautiful CLI for common Odoo module operations.",
    no_args_is_help=False,
)
console = Console()


def _resolve_or_exit(config_path, database):
    # type: (Optional[str], Optional[str]) -> object
    try:
        return resolve_config(config_path, database)
    except (FileNotFoundError, ValueError) as e:
        console.print(Panel(f"[red]{e}[/]", title="[bold red]Error[/]", border_style="red"))
        raise typer.Exit(1)


def _show_result(result):
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


def _run_command(label, action_fn, module, config_path, database):
    cfg = _resolve_or_exit(config_path, database)
    with console.status(
        f"  [bold cyan]{label}[/] [yellow]{module}[/] on [bold]{cfg.db_name}[/]...",
        spinner="dots",
    ):
        result = action_fn(cfg, module)
    _show_result(result)


def _run_simple(label, action_fn, config_path, database):
    cfg = _resolve_or_exit(config_path, database)
    with console.status(f"  [bold cyan]{label}[/] on [bold]{cfg.db_name}[/]...", spinner="dots"):
        result = action_fn(cfg)
    _show_result(result)


# ---------------------------------------------------------------------------
# Original commands
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# New commands
# ---------------------------------------------------------------------------

@app.command("update-list")
def update_list(
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to odoo.conf (default: ./odoo.conf)."),
    database: Optional[str] = typer.Option(None, "--database", "-d", help="Database name (overrides odoo.conf)."),
) -> None:
    """Update the list of available modules."""
    _run_simple("Updating module list", update_list_cmd_fn, config, database)


@app.command()
def info(
    module: str = typer.Option(..., "--module", "-m", help="Technical name of the Odoo module."),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to odoo.conf (default: ./odoo.conf)."),
    database: Optional[str] = typer.Option(None, "--database", "-d", help="Database name (overrides odoo.conf)."),
) -> None:
    """Show detailed information about a module."""
    cfg = _resolve_or_exit(config, database)
    with console.status(
        f"  [bold cyan]Fetching info[/] for [yellow]{module}[/] on [bold]{cfg.db_name}[/]...",
        spinner="dots",
    ):
        result = module_info_cmd_fn(cfg, module)

    if not result.success:
        console.print(Panel(f"[red]{result.message}[/]", title="[bold red]Failed[/]", border_style="red"))
        raise typer.Exit(1)

    _render_module_info(result.data)


@app.command("list")
def list_cmd(
    installed: bool = typer.Option(False, "--installed", help="Show only installed modules."),
    uninstalled: bool = typer.Option(False, "--uninstalled", help="Show only uninstalled modules."),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to odoo.conf (default: ./odoo.conf)."),
    database: Optional[str] = typer.Option(None, "--database", "-d", help="Database name (overrides odoo.conf)."),
) -> None:
    """List modules, optionally filtered by state."""
    state_filter = "all"
    if installed:
        state_filter = "installed"
    elif uninstalled:
        state_filter = "uninstalled"

    cfg = _resolve_or_exit(config, database)
    with console.status(
        f"  [bold cyan]Listing modules[/] on [bold]{cfg.db_name}[/]...",
        spinner="dots",
    ):
        result = list_modules_cmd_fn(cfg, state_filter)

    if not result.success:
        console.print(Panel(f"[red]{result.message}[/]", title="[bold red]Failed[/]", border_style="red"))
        raise typer.Exit(1)

    _render_module_list(result.data, result.message)


@app.command("clear-assets")
def clear_assets(
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to odoo.conf (default: ./odoo.conf)."),
    database: Optional[str] = typer.Option(None, "--database", "-d", help="Database name (overrides odoo.conf)."),
) -> None:
    """Delete compiled CSS/JS asset bundles."""
    _run_simple("Clearing assets", clear_assets_cmd_fn, config, database)


@app.command("reset-password")
def reset_password(
    user: str = typer.Option("admin", "--user", "-u", help="Login of the user (default: admin)."),
    password: str = typer.Option("admin", "--password", "-p", help="New password (default: admin)."),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to odoo.conf (default: ./odoo.conf)."),
    database: Optional[str] = typer.Option(None, "--database", "-d", help="Database name (overrides odoo.conf)."),
) -> None:
    """Reset a user's password."""
    cfg = _resolve_or_exit(config, database)
    with console.status(
        f"  [bold cyan]Resetting password[/] for [yellow]{user}[/] on [bold]{cfg.db_name}[/]...",
        spinner="dots",
    ):
        result = reset_password_cmd_fn(cfg, user, password)
    _show_result(result)


@app.command("shell-exec")
def shell_exec(
    file: str = typer.Option(..., "--file", "-f", help="Path to a .py file to execute in odoo shell."),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to odoo.conf (default: ./odoo.conf)."),
    database: Optional[str] = typer.Option(None, "--database", "-d", help="Database name (overrides odoo.conf)."),
) -> None:
    """Run an arbitrary Python script through odoo shell."""
    script_path = Path(file)
    if not script_path.is_file():
        console.print(Panel(f"[red]File not found: {file}[/]", title="[bold red]Error[/]", border_style="red"))
        raise typer.Exit(1)

    script_content = script_path.read_text(encoding="utf-8")
    cfg = _resolve_or_exit(config, database)

    with console.status(
        f"  [bold cyan]Running[/] [yellow]{script_path.name}[/] on [bold]{cfg.db_name}[/]...",
        spinner="dots",
    ):
        result = shell_exec_cmd_fn(cfg, script_content)
    _show_result(result)


@app.command()
def scaffold(
    module: str = typer.Option(..., "--module", "-m", help="Technical name for the new module."),
    path: str = typer.Option(".", "--path", "-p", help="Directory where the module will be created (default: current)."),
) -> None:
    """Generate a new Odoo module skeleton."""
    from odoo_rich_cli.scaffold import create_module

    try:
        created_path = create_module(module, path)
    except FileExistsError as e:
        console.print(Panel(f"[red]{e}[/]", title="[bold red]Error[/]", border_style="red"))
        raise typer.Exit(1)

    console.print(Panel(
        f"[green]Module created at [bold]{created_path}[/][/]",
        title="[bold green]Scaffolded[/]",
        border_style="green",
    ))


# ---------------------------------------------------------------------------
# Rich rendering helpers
# ---------------------------------------------------------------------------

def _render_module_info(data):
    if not data:
        return

    STATE_COLORS = {
        "installed": "green",
        "uninstalled": "dim",
        "to upgrade": "yellow",
        "to install": "cyan",
        "to remove": "red",
    }

    state = data.get("state", "")
    color = STATE_COLORS.get(state, "white")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold", width=16)
    table.add_column()

    table.add_row("Name", data.get("name", ""))
    table.add_row("Technical Name", data.get("technical_name", ""))
    table.add_row("State", f"[{color}]{state}[/]")
    table.add_row("Version", data.get("version", ""))
    table.add_row("Author", data.get("author", ""))
    table.add_row("Summary", data.get("summary", ""))

    deps = data.get("dependencies", [])
    table.add_row("Dependencies", ", ".join(deps) if deps else "[dim]none[/]")

    rev_deps = data.get("reverse_dependencies", [])
    table.add_row("Dependents", ", ".join(rev_deps) if rev_deps else "[dim]none[/]")

    console.print(Panel(table, title="[bold]Module Info[/]", border_style="bright_blue", padding=(1, 2)))


def _render_module_list(data, message):
    if not data:
        console.print(Panel(f"[yellow]{message}[/]", title="[bold yellow]Result[/]", border_style="yellow"))
        return

    STATE_COLORS = {
        "installed": "green",
        "uninstalled": "dim",
        "to upgrade": "yellow",
        "to install": "cyan",
        "to remove": "red",
    }

    table = Table(title=message, border_style="bright_blue", header_style="bold")
    table.add_column("#", style="dim", width=5, justify="right")
    table.add_column("Technical Name", style="bold")
    table.add_column("Name")
    table.add_column("State")
    table.add_column("Version", style="dim")

    for i, m in enumerate(data, 1):
        state = m.get("state", "")
        color = STATE_COLORS.get(state, "white")
        table.add_row(
            str(i),
            m.get("technical_name", ""),
            m.get("name", ""),
            f"[{color}]{state}[/]",
            m.get("version", ""),
        )

    console.print(table)


# ---------------------------------------------------------------------------
# Callback — interactive menu when no subcommand given
# ---------------------------------------------------------------------------

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
