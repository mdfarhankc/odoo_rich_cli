# Odoo Rich CLI

A beautiful CLI tool for common Odoo module operations — install, upgrade, and uninstall — without manually typing ORM code in `odoo shell`.

Compatible with **Odoo 14+** and **Python 3.7+**.

## Features

- **Direct commands** — run `odoo-cli install -m sale` straight from your terminal
- **Interactive menu** — run `odoo-cli` with no arguments for a guided Rich UI
- **Reads odoo.conf** — auto-detects database and config from your project directory
- **Rich output** — spinners, colored success/error messages, clean formatting

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

Run commands from a directory that contains an `odoo.conf` file (or pass `--config` explicitly).

### Direct commands

```bash
# Install a module
odoo-cli install -m sale

# Upgrade a module
odoo-cli upgrade -m sale

# Uninstall a module
odoo-cli uninstall -m sale
```

### Override database or config path

```bash
odoo-cli install -m sale -d my_database
odoo-cli upgrade -m sale -c /path/to/odoo.conf
odoo-cli uninstall -m sale -c /path/to/odoo.conf -d my_database
```

### Interactive menu

```bash
odoo-cli
```

This launches a numbered menu where you can pick an operation, enter the module name, and optionally override the config path and database.

## How it works

The CLI builds Python ORM scripts and pipes them into `odoo shell -c <conf> -d <db> --no-http` via subprocess. Each script locates the module, calls the appropriate `button_immediate_*` method, and runs `env.cr.commit()` so changes persist after the shell exits.

## Testing locally

### Prerequisites

- An Odoo instance with a PostgreSQL database already set up
- The `odoo` command available on your PATH (e.g. via an Odoo source checkout or pip install)
- An `odoo.conf` file

### 1. Install in editable mode

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

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

# Test the interactive menu (does not require a running Odoo)
odoo-cli

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
│   ├── shell.py                # Pipes scripts into odoo shell subprocess
│   ├── commands.py             # Builds ORM scripts for install/upgrade/uninstall
│   ├── app.py                  # Typer CLI app with subcommands
│   └── menu.py                 # Rich interactive menu
```

## License

MIT
