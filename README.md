# Odoo Rich CLI

A beautiful CLI tool for managing Odoo modules — install, upgrade, and uninstall — with a Rich UI and Typer, without manually typing ORM code in `odoo shell`.

Compatible with **Odoo 14+** and **Python 3.7+**.

## Features

- **Direct commands** — run `odoo-cli install -m sale` straight from your terminal
- **Interactive menu** — run `odoo-cli` with no arguments for a guided Rich UI with ASCII banner, config status, and colored output
- **Global flags** — pass `-c` and `-d` at the top level, works for both direct commands and interactive mode
- **Auto-detects Odoo** — finds `odoo`, `odoo-bin` on PATH, or `./odoo-bin` in the current directory
- **Uses your active virtualenv** — runs `odoo-bin` with the currently active Python interpreter, so all your Odoo dependencies are available
- **Reads odoo.conf** — auto-detects database and config from your project directory

## Installation

### From source (with pip)

```bash
pip install .
```

### From source (with uv)

```bash
uv pip install .
```

## Usage

Run commands from your Odoo project directory (where `odoo.conf` or `odoo-bin` lives), with your Odoo virtualenv activated.

### Direct commands

```bash
# Install a module
odoo-cli install -m sale

# Upgrade a module
odoo-cli upgrade -m sale

# Uninstall a module
odoo-cli uninstall -m sale
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

This launches a Rich interactive menu with:
- ASCII art banner and version info
- Config/database status panel (auto-detected from `odoo.conf`)
- Numbered operations to choose from
- Spinner and colored result output

If config was auto-detected, you won't be prompted for it again. If not, the menu will ask you for the config path and database.

## How it works

1. The CLI finds the Odoo command (`odoo`, `odoo-bin`, or `./odoo-bin`) and runs it using your currently active Python interpreter (`sys.executable`)
2. It builds Python ORM scripts and pipes them into `odoo shell -c <conf> -d <db> --no-http` via subprocess
3. Each script locates the module, calls the appropriate `button_immediate_*` method, and runs `env.cr.commit()` so changes persist after the shell exits
4. Output is parsed via a sentinel marker for reliable result extraction from odoo shell's startup noise

## Testing locally

### Prerequisites

- An Odoo instance with a PostgreSQL database already set up
- `odoo` or `odoo-bin` available (on PATH or in the current directory)
- An `odoo.conf` file
- Your Odoo virtualenv activated (so all dependencies like `PyPDF2`, etc. are available)

### 1. Install in editable mode

Install `odoo-cli` into your Odoo virtualenv so everything shares the same environment:

```bash
# Using pip
pip install -e .

# Or using uv
uv pip install -e .
```

With editable mode (`-e`), code changes are picked up immediately — no need to reinstall after every edit.

### 2. Create a minimal odoo.conf (if you don't have one)

```ini
[options]
db_name = my_odoo_db
addons_path = /path/to/odoo/addons
```

### 3. Run from the directory containing odoo.conf

```bash
# Test the help output
odoo-cli --help
odoo-cli install --help

# Launch the interactive menu
odoo-cli

# Launch with a specific config file
odoo-cli -c ./local-odoo.conf

# Test actual module operations against your database
odoo-cli install -m sale
odoo-cli upgrade -m sale
odoo-cli uninstall -m sale
```

### 4. Test with explicit flags

```bash
# Point to a specific config and database
odoo-cli install -m sale -c /path/to/odoo.conf -d testdb
```

### 5. Test error handling

```bash
# Missing odoo.conf (run from a directory without one)
cd /tmp && odoo-cli install -m sale

# Missing module name
odoo-cli install

# Non-existent module
odoo-cli install -m this_module_does_not_exist
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
│   ├── commands.py             # Builds ORM scripts for install/upgrade/uninstall
│   ├── app.py                  # Typer CLI app with global flags and subcommands
│   └── menu.py                 # Rich interactive menu with banner and config status
```

## License

MIT
