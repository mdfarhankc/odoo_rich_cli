from odoo_rich_cli.config import OdooConfig
from odoo_rich_cli.shell import ShellResult, execute


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
