# Contributing to Odoo Rich CLI

Thanks for your interest in contributing. This is a small developer tool, so the process is straightforward.

## Getting started

1. Fork the repository on GitHub.
2. Clone your fork:

```bash
git clone https://github.com/<your-username>/odoo_rich_cli.git
cd odoo_rich_cli
```

3. Create a branch off `main`:

```bash
git checkout -b my-feature main
```

## Setting up the dev environment

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

1. Activate your Odoo virtualenv (the CLI needs Odoo's dependencies at runtime).
2. Install the package in editable mode:

```bash
pip install -e .
# or
uv pip install -e .
```

Editable mode means your code changes take effect immediately without reinstalling.

## Running and testing locally

You need a working Odoo instance with a PostgreSQL database and an `odoo.conf` file.

```bash
# Verify the CLI loads
odoo-cli --help

# Test interactive mode
odoo-cli

# Test direct commands against your database
odoo-cli install -m sale
odoo-cli upgrade -m sale
odoo-cli uninstall -m sale
```

See the README's "Testing locally" section for more detail.

## Code style

There is no linter or formatter configured. Just write clean, readable Python:

- Keep functions short and focused.
- Use type hints where practical (compatible with Python 3.7+).
- Follow existing patterns in the codebase.
- No unused imports or dead code.

## Submitting a pull request

1. Make sure your branch is up to date with `main`.
2. Write clear, descriptive commit messages.
3. Open a pull request against `main`.
4. Describe what your change does and why.

Keep PRs small and focused on a single change when possible.

## Reporting bugs

Open an issue and include:

- Steps to reproduce the problem.
- The error message or unexpected behavior.
- Your Odoo version (14, 15, 16, 17, 18, ...).
- Your Python version.
- Your OS.

## Feature requests

Feature requests are welcome. Open an issue describing the use case and what you'd like to see. Discussion before implementation helps avoid wasted effort.
