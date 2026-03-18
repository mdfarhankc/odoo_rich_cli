import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SENTINEL = "__ODOO_CLI_RESULT__:"


def _find_odoo_command():
    """Find a working odoo command.

    Always uses sys.executable (the currently active Python interpreter)
    so that odoo-bin runs in the same virtualenv the user activated.
    """
    python = sys.executable

    # Check for odoo / odoo-bin scripts on PATH
    for cmd in ["odoo", "odoo-bin"]:
        found = shutil.which(cmd)
        if found:
            # Run through the current interpreter to guarantee the right venv
            return [python, found]

    # Check for odoo-bin in the current working directory (common source setup)
    local_bin = Path.cwd() / "odoo-bin"
    if local_bin.is_file():
        return [python, str(local_bin)]

    return None


@dataclass
class ShellResult:
    success: bool
    message: str
    stdout: str
    stderr: str
    return_code: int


def _wrap_script(script: str) -> str:
    """Wrap a script with try/except and sentinel output for reliable parsing."""
    return f"""\
import json as _json

try:
{_indent(script, 4)}
    _result = {{"ok": True, "message": "Operation completed successfully."}}
except Exception as _e:
    _result = {{"ok": False, "message": str(_e)}}

print("{SENTINEL}" + _json.dumps(_result))
"""


def _indent(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line.strip() else line for line in text.splitlines())


def execute(
    script: str,
    config_path: str,
    database: str,
    timeout: int = 120,
) -> ShellResult:
    """Run a Python script inside `odoo shell` and return the parsed result."""
    wrapped = _wrap_script(script)

    odoo_cmd = _find_odoo_command()
    if odoo_cmd is None:
        return ShellResult(
            success=False,
            message=(
                "Could not find 'odoo' or 'odoo-bin' on your PATH or in the current directory. "
                "Make sure your Odoo virtualenv is activated."
            ),
            stdout="",
            stderr="",
            return_code=-1,
        )

    cmd = odoo_cmd + [
        "shell",
        "-c", config_path,
        "-d", database,
        "--no-http",
    ]

    try:
        proc = subprocess.run(
            cmd,
            input=wrapped,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return ShellResult(
            success=False,
            message=(
                "Could not find 'odoo' or 'odoo-bin' on your PATH or in the current directory. "
                "Make sure your Odoo virtualenv is activated."
            ),
            stdout="",
            stderr="",
            return_code=-1,
        )
    except subprocess.TimeoutExpired:
        return ShellResult(
            success=False,
            message=f"Command timed out after {timeout} seconds.",
            stdout="",
            stderr="",
            return_code=-1,
        )

    # Parse sentinel from stdout
    for line in proc.stdout.splitlines():
        if line.startswith(SENTINEL):
            payload = line[len(SENTINEL):]
            try:
                data = json.loads(payload)
                return ShellResult(
                    success=data.get("ok", False),
                    message=data.get("message", ""),
                    stdout=proc.stdout,
                    stderr=proc.stderr,
                    return_code=proc.returncode,
                )
            except json.JSONDecodeError:
                break

    # Sentinel not found — treat as failure
    return ShellResult(
        success=proc.returncode == 0,
        message=proc.stderr.strip() or "No structured output received from odoo shell.",
        stdout=proc.stdout,
        stderr=proc.stderr,
        return_code=proc.returncode,
    )
