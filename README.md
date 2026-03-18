# Odoo Rich CLI

A beautiful CLI tool for managing Odoo modules with a Rich UI and Typer — without manually typing ORM code in `odoo shell`.

Compatible with **Odoo 14+** and **Python 3.7+**.

## Features

- **10 commands** — install, upgrade, uninstall, update-list, info, list, clear-assets, reset-password, scaffold, shell-exec
- **Interactive menu** — run `odoo-cli` with no arguments for a guided Rich UI
- **Global flags** — pass `-c` and `-d` at the top level, works for both direct commands and interactive mode
- **Auto-detects Odoo** — finds `odoo`, `odoo-bin` on PATH, or `./odoo-bin` in the current directory
- **Uses your active virtualenv** — runs `odoo-bin` with the currently active Python interpreter
- **Reads odoo.conf** — auto-detects database and config from your project directory

## Installation

```bash
pip install odoo-rich-cli
```

## Commands

| Command | Description |
|---|---|
| `install -m <module>` | Install a module |
| `upgrade -m <module>` | Upgrade an installed module |
| `uninstall -m <module>` | Uninstall a module |
| `update-list` | Refresh the list of available modules |
| `info -m <module>` | Show module details (state, version, dependencies, dependents) |
| `list` | List modules (with `--installed` or `--uninstalled` filter) |
| `clear-assets` | Delete compiled CSS/JS asset bundles |
| `reset-password` | Reset a user's password (default: admin/admin) |
| `scaffold -m <module>` | Generate a new module skeleton |
| `shell-exec -f <script.py>` | Run an arbitrary Python script through odoo shell |

## Usage

Run commands from your Odoo project directory (where `odoo.conf` or `odoo-bin` lives), with your Odoo virtualenv activated.

### Module operations

```bash
odoo-cli install -m sale
odoo-cli upgrade -m sale
odoo-cli uninstall -m sale
```

### Module discovery

```bash
# Refresh module list (required before installing new modules)
odoo-cli update-list

# Show details about a module
odoo-cli info -m sale

# List all installed modules
odoo-cli list --installed

# List all modules
odoo-cli list
```

### Maintenance

```bash
# Clear compiled CSS/JS assets (fixes "my styles aren't updating")
odoo-cli clear-assets

# Reset admin password to "admin"
odoo-cli reset-password

# Reset a specific user's password
odoo-cli reset-password -u john -p newpass123
```

### Development

```bash
# Generate a new module skeleton
odoo-cli scaffold -m my_custom_module

# Generate in a specific directory
odoo-cli scaffold -m my_custom_module -p ./addons

# Run a custom script through odoo shell
odoo-cli shell-exec -f fix_data.py
```

### Global flags

The `-c` (config) and `-d` (database) flags work at the top level and on every subcommand:

```bash
# Launch interactive menu with a specific config
odoo-cli -c ./local-odoo.conf

# Direct command with config and database override
odoo-cli install -m sale -c /path/to/odoo.conf -d my_database
```

### Interactive menu

```bash
odoo-cli
```

Launches a Rich interactive menu with an ASCII banner, config status panel, and numbered operations. If config was auto-detected, you won't be prompted for it again.

## How it works

1. The CLI finds the Odoo command (`odoo`, `odoo-bin`, or `./odoo-bin`) and runs it using your currently active Python interpreter (`sys.executable`)
2. It builds Python ORM scripts and pipes them into `odoo shell -c <conf> -d <db> --no-http` via subprocess
3. Each script runs the operation and calls `env.cr.commit()` so changes persist after the shell exits
4. Output is parsed via a sentinel marker for reliable result extraction from odoo shell's startup noise

## Testing locally

### Prerequisites

- An Odoo instance with a PostgreSQL database already set up
- `odoo` or `odoo-bin` available (on PATH or in the current directory)
- An `odoo.conf` file
- Your Odoo virtualenv activated (so all dependencies are available)

### Install in editable mode

Install `odoo-cli` into your Odoo virtualenv so everything shares the same environment:

```bash
pip install -e .
```

With editable mode (`-e`), code changes are picked up immediately — no need to reinstall after every edit.

### Test commands

```bash
# Verify the CLI loads
odoo-cli --help

# Test interactive menu
odoo-cli

# Test against your database
odoo-cli update-list
odoo-cli list --installed
odoo-cli info -m sale
odoo-cli install -m sale
odoo-cli upgrade -m sale
odoo-cli clear-assets
odoo-cli reset-password
odoo-cli scaffold -m test_module -p /tmp
```

## Project structure

```
odoo_rich_cli/
├── pyproject.toml              # Project metadata, dependencies, entry point
├── main.py                     # Thin entry point: python main.py
├── odoo_rich_cli/
│   ├── __init__.py             # Package version
│   ├── config.py               # Finds and parses odoo.conf
│   ├── shell.py                # Auto-detects odoo command, pipes scripts into odoo shell
│   ├── commands.py             # ORM scripts for all shell-based commands
│   ├── scaffold.py             # Module skeleton generator (pure file creation)
│   ├── app.py                  # Typer CLI app with all commands
│   └── menu.py                 # Rich interactive menu
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on setting up the dev environment, submitting PRs, and reporting bugs.

## License

MIT — see [LICENSE](LICENSE) for details.
