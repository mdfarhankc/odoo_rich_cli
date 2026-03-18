from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from odoo_rich_cli import __version__
from odoo_rich_cli.commands import (
    install_module,
    upgrade_module,
    uninstall_module,
    update_list,
    module_info,
    list_modules,
    clear_assets,
    reset_password,
)
from odoo_rich_cli.config import resolve_config

console = Console()

# (key, name, description, function, action_label, prompt_type)
# prompt_type: "module", "none", "list_filter", "password"
ACTIONS = [
    ("1", "Install",         "Download and install a module",       install_module,  "Installing",      "module"),
    ("2", "Upgrade",         "Upgrade an installed module",         upgrade_module,  "Upgrading",       "module"),
    ("3", "Uninstall",       "Remove an installed module",          uninstall_module,"Uninstalling",    "module"),
    ("4", "Update List",     "Refresh available modules list",      update_list,     "Updating list",   "none"),
    ("5", "Module Info",     "Show details about a module",         module_info,     "Fetching info",   "module"),
    ("6", "List Modules",    "List modules by state",               list_modules,    "Listing",         "list_filter"),
    ("7", "Clear Assets",    "Delete compiled asset bundles",       clear_assets,    "Clearing assets", "none"),
    ("8", "Reset Password",  "Reset a user's password",             reset_password,  "Resetting",       "password"),
]

BANNER = r"""
   ____     __               ________    ____
  / __ \___/ /___  ___      / ___/ /    /  _/
 / /_/ / _  / __ \/ __ \   / /  / /    _/ /
 \____/\_,_/\____/\____/  /___/_/____/___/
"""


def _show_header():
    banner_text = Text(BANNER, style="bold purple")
    console.print(
        Panel(
            banner_text,
            subtitle=f"[dim]v{__version__}[/]",
            border_style="bright_blue",
            padding=(0, 2),
        )
    )


def _show_config_status(config_path, database):
    # type: (Optional[str], Optional[str]) -> object
    try:
        cfg = resolve_config(config_path, database)
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column(style="dim", width=10)
        table.add_column(style="bold")
        table.add_row("Config", str(cfg.config_path))
        table.add_row("Database", cfg.db_name)
        console.print(
            Panel(table, title="[bold green]Connected[/]", border_style="green", padding=(0, 2))
        )
        return cfg
    except (FileNotFoundError, ValueError) as e:
        console.print(
            Panel(f"[yellow]{e}[/]", title="[bold yellow]No Config[/]", border_style="yellow", padding=(0, 2))
        )
        return None


def _show_menu():
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold cyan", width=6, justify="center")
    table.add_column(style="bold white", width=18)
    table.add_column(style="dim")

    for key, name, desc, *_ in ACTIONS:
        table.add_row(f"[{key}]", name, desc)

    table.add_row("")
    table.add_row("[0]", "Exit", "Quit the CLI")

    console.print(
        Panel(table, title="[bold]Operations[/]", border_style="bright_blue", padding=(1, 2))
    )


def _show_result(success, message):
    # type: (bool, str) -> None
    if success:
        console.print(
            Panel(f"[green]{message}[/]", title="[bold green]Success[/]", border_style="green", padding=(0, 2))
        )
    else:
        console.print(
            Panel(f"[red]{message}[/]", title="[bold red]Failed[/]", border_style="red", padding=(0, 2))
        )


def _render_module_info(data):
    """Render module info as a Rich panel (reused from app.py logic)."""
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
    """Render module list as a Rich table."""
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


def _get_config(cached_cfg, config_path, database):
    """Return cached config or prompt the user for config/database."""
    if cached_cfg is not None:
        return cached_cfg

    cp = console.input("  [bold]Config path[/] [dim](Enter for ./odoo.conf):[/] ").strip() or None
    db = console.input("  [bold]Database:[/] ").strip() or None
    return resolve_config(cp, db)


def interactive_menu(
    config_path=None,  # type: Optional[str]
    database=None,     # type: Optional[str]
):
    # type: (...) -> None
    console.clear()
    _show_header()

    cached_cfg = _show_config_status(config_path, database)

    while True:
        console.print()
        _show_menu()

        choice = console.input("\n  [bold bright_blue]>[/] ").strip()

        if choice == "0":
            console.print()
            console.print(Rule("[dim]Goodbye[/]", style="dim"))
            console.print()
            raise typer.Exit()

        action_map = {key: (fn, label, ptype) for key, _, _, fn, label, ptype in ACTIONS}
        if choice not in action_map:
            console.print("  [red]Invalid choice.[/]")
            continue

        action_fn, action_label, prompt_type = action_map[choice]

        console.print()
        console.print(Rule(style="dim"))

        # Gather inputs based on prompt type
        try:
            cfg = _get_config(cached_cfg, config_path, database)
        except (FileNotFoundError, ValueError) as e:
            _show_result(False, str(e))
            continue

        if prompt_type == "module":
            module = console.input("  [bold]Module name:[/] ").strip()
            if not module:
                console.print("  [red]Module name cannot be empty.[/]")
                continue

            console.print()
            with console.status(
                f"  [bold cyan]{action_label}[/] [yellow]{module}[/] on [bold]{cfg.db_name}[/]...",
                spinner="dots",
            ):
                result = action_fn(cfg, module)

            # Special rendering for info command
            if action_fn is module_info and result.success and result.data:
                _render_module_info(result.data)
            else:
                _show_result(result.success, result.message)

        elif prompt_type == "none":
            console.print()
            with console.status(
                f"  [bold cyan]{action_label}[/] on [bold]{cfg.db_name}[/]...",
                spinner="dots",
            ):
                result = action_fn(cfg)
            _show_result(result.success, result.message)

        elif prompt_type == "list_filter":
            console.print("  [bold]Filter:[/] [dim](1) All  (2) Installed  (3) Uninstalled[/]")
            filter_choice = console.input("  [bold bright_blue]>[/] ").strip()
            filter_map = {"1": "all", "2": "installed", "3": "uninstalled"}
            state_filter = filter_map.get(filter_choice, "all")

            console.print()
            with console.status(
                f"  [bold cyan]Listing modules[/] on [bold]{cfg.db_name}[/]...",
                spinner="dots",
            ):
                result = action_fn(cfg, state_filter)

            if result.success and result.data:
                _render_module_list(result.data, result.message)
            else:
                _show_result(result.success, result.message)

        elif prompt_type == "password":
            user = console.input("  [bold]User login[/] [dim](Enter for admin):[/] ").strip() or "admin"
            pw = console.input("  [bold]New password[/] [dim](Enter for admin):[/] ").strip() or "admin"

            console.print()
            with console.status(
                f"  [bold cyan]Resetting password[/] for [yellow]{user}[/] on [bold]{cfg.db_name}[/]...",
                spinner="dots",
            ):
                result = action_fn(cfg, user, pw)
            _show_result(result.success, result.message)
