from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from odoo_rich_cli import __version__
from odoo_rich_cli.commands import install_module, upgrade_module, uninstall_module
from odoo_rich_cli.config import resolve_config

console = Console()

ACTIONS = [
    ("1", "Install", "Download and install a module", install_module, "Installing"),
    ("2", "Upgrade", "Upgrade an installed module", upgrade_module, "Upgrading"),
    ("3", "Uninstall", "Remove an installed module", uninstall_module, "Uninstalling"),
]

BANNER = r"""
   ____     __               ________    ____
  / __ \___/ /___  ___      / ___/ /    /  _/
 / /_/ / _  / __ \/ __ \   / /  / /    _/ /
 \____/\_,_/\____/\____/  /___/_/____/___/
"""


def _show_header() -> None:
    banner_text = Text(BANNER, style="bold purple")
    console.print(
        Panel(
            banner_text,
            subtitle=f"[dim]v{__version__}[/]",
            border_style="bright_blue",
            padding=(0, 2),
        )
    )


def _show_config_status(
    config_path,   # type: Optional[str]
    database,      # type: Optional[str]
) -> None:
    try:
        cfg = resolve_config(config_path, database)
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column(style="dim", width=10)
        table.add_column(style="bold")
        table.add_row("Config", str(cfg.config_path))
        table.add_row("Database", cfg.db_name)
        console.print(
            Panel(
                table,
                title="[bold green]Connected[/]",
                border_style="green",
                padding=(0, 2),
            )
        )
        return cfg
    except (FileNotFoundError, ValueError) as e:
        console.print(
            Panel(
                f"[yellow]{e}[/]",
                title="[bold yellow]No Config[/]",
                border_style="yellow",
                padding=(0, 2),
            )
        )
        return None


def _show_menu() -> None:
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold cyan", width=6, justify="center")
    table.add_column(style="bold white", width=14)
    table.add_column(style="dim")

    for key, name, desc, *_ in ACTIONS:
        table.add_row(f"[{key}]", name, desc)

    table.add_row("")
    table.add_row("[0]", "Exit", "Quit the CLI")

    console.print(
        Panel(
            table,
            title="[bold]Operations[/]",
            border_style="bright_blue",
            padding=(1, 2),
        )
    )


def _show_result(success, message):
    # type: (bool, str) -> None
    if success:
        console.print(
            Panel(
                f"[green]{message}[/]",
                title="[bold green]Success[/]",
                border_style="green",
                padding=(0, 2),
            )
        )
    else:
        console.print(
            Panel(
                f"[red]{message}[/]",
                title="[bold red]Failed[/]",
                border_style="red",
                padding=(0, 2),
            )
        )


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

        action_map = {key: (fn, label) for key, _, _, fn, label in ACTIONS}
        if choice not in action_map:
            console.print("  [red]Invalid choice.[/]")
            continue

        action_fn, action_label = action_map[choice]

        console.print()
        console.print(Rule(style="dim"))
        module = console.input("  [bold]Module name:[/] ").strip()
        if not module:
            console.print("  [red]Module name cannot be empty.[/]")
            continue

        # Only ask for config/db if we couldn't auto-detect earlier
        cfg = cached_cfg
        if cfg is None:
            cp = console.input("  [bold]Config path[/] [dim](Enter for ./odoo.conf):[/] ").strip() or None
            db = console.input("  [bold]Database:[/] ").strip() or None
            try:
                cfg = resolve_config(cp, db)
            except (FileNotFoundError, ValueError) as e:
                _show_result(False, str(e))
                continue

        console.print()
        with console.status(
            f"  [bold cyan]{action_label}[/] [yellow]{module}[/] on [bold]{cfg.db_name}[/]...",
            spinner="dots",
        ):
            result = action_fn(cfg, module)

        _show_result(result.success, result.message)
