from odoo_rich_cli.config import OdooConfig
from odoo_rich_cli.shell import ShellResult, execute


# ---------------------------------------------------------------------------
# Module install / upgrade / uninstall
# ---------------------------------------------------------------------------

def _module_script(module_name: str, action: str, action_label: str) -> str:
    """Build an ORM script that performs an action on a module."""
    return f"""\
module = env["ir.module.module"].search([("name", "=", "{module_name}")], limit=1)
if not module:
    raise Exception("Module '{module_name}' not found in the database.")
module.{action}()
env.cr.commit()
_result = {{"ok": True, "message": "Module '{module_name}' {action_label} successfully."}}"""


def install_module(config: OdooConfig, module_name: str) -> ShellResult:
    script = _module_script(module_name, "button_immediate_install", "installed")
    return execute(script, config.config_path_str, config.db_name)


def upgrade_module(config: OdooConfig, module_name: str) -> ShellResult:
    script = _module_script(module_name, "button_immediate_upgrade", "upgraded")
    return execute(script, config.config_path_str, config.db_name)


def uninstall_module(config: OdooConfig, module_name: str) -> ShellResult:
    script = _module_script(module_name, "button_immediate_uninstall", "uninstalled")
    return execute(script, config.config_path_str, config.db_name)


# ---------------------------------------------------------------------------
# Update module list
# ---------------------------------------------------------------------------

def update_list(config: OdooConfig) -> ShellResult:
    script = """\
env["ir.module.module"].update_list()
env.cr.commit()
_result = {"ok": True, "message": "Module list updated successfully."}"""
    return execute(script, config.config_path_str, config.db_name)


# ---------------------------------------------------------------------------
# Module info
# ---------------------------------------------------------------------------

def module_info(config: OdooConfig, module_name: str) -> ShellResult:
    script = f"""\
module = env["ir.module.module"].search([("name", "=", "{module_name}")], limit=1)
if not module:
    raise Exception("Module '{module_name}' not found in the database.")
deps = [d.name for d in module.dependencies_id]
rev_deps = env["ir.module.module.dependency"].search([
    ("name", "=", module.name),
])
rev_dep_names = [d.module_id.name for d in rev_deps]
_result = {{
    "ok": True,
    "message": "Module info retrieved.",
    "data": {{
        "name": module.shortdesc or module.name,
        "technical_name": module.name,
        "state": module.state,
        "version": module.installed_version or module.latest_version or "",
        "author": module.author or "",
        "summary": module.summary or "",
        "dependencies": deps,
        "reverse_dependencies": rev_dep_names,
    }},
}}"""
    return execute(script, config.config_path_str, config.db_name)


# ---------------------------------------------------------------------------
# List modules
# ---------------------------------------------------------------------------

def list_modules(config: OdooConfig, state_filter: str = "all") -> ShellResult:
    if state_filter == "installed":
        domain = '[("state", "=", "installed")]'
    elif state_filter == "uninstalled":
        domain = '[("state", "=", "uninstalled")]'
    else:
        domain = "[]"

    script = f"""\
modules = env["ir.module.module"].search({domain}, order="name")
_result = {{
    "ok": True,
    "message": str(len(modules)) + " module(s) found.",
    "data": [
        {{
            "name": m.shortdesc or m.name,
            "technical_name": m.name,
            "state": m.state,
            "version": m.installed_version or m.latest_version or "",
        }}
        for m in modules
    ],
}}"""
    return execute(script, config.config_path_str, config.db_name, timeout=180)


# ---------------------------------------------------------------------------
# Clear assets
# ---------------------------------------------------------------------------

def clear_assets(config: OdooConfig) -> ShellResult:
    script = """\
assets = env["ir.attachment"].search([
    ("name", "like", ".assets_"),
    ("res_model", "=", "ir.ui.view"),
])
count = len(assets)
if count:
    assets.unlink()
    env.cr.commit()
_result = {"ok": True, "message": str(count) + " asset(s) deleted."}"""
    return execute(script, config.config_path_str, config.db_name)


# ---------------------------------------------------------------------------
# Reset password
# ---------------------------------------------------------------------------

def reset_password(config: OdooConfig, user: str = "admin", password: str = "admin") -> ShellResult:
    # Escape single quotes in user/password to prevent script breakage
    safe_user = user.replace("\\", "\\\\").replace("'", "\\'")
    safe_pass = password.replace("\\", "\\\\").replace("'", "\\'")
    script = f"""\
user_rec = env["res.users"].search([("login", "=", '{safe_user}')], limit=1)
if not user_rec:
    raise Exception("User '{safe_user}' not found.")
user_rec.password = '{safe_pass}'
env.cr.commit()
_result = {{"ok": True, "message": "Password for '{safe_user}' reset successfully."}}"""
    return execute(script, config.config_path_str, config.db_name)


# ---------------------------------------------------------------------------
# Shell exec (arbitrary script)
# ---------------------------------------------------------------------------

def shell_exec(config: OdooConfig, script_content: str) -> ShellResult:
    return execute(script_content, config.config_path_str, config.db_name, timeout=300)
