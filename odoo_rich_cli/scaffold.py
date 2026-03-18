import os
from pathlib import Path


def create_module(module_name: str, path: str = ".") -> str:
    """Generate an Odoo module skeleton. Returns the path to the created module."""
    base = Path(path) / module_name

    if base.exists():
        raise FileExistsError(f"Directory '{base}' already exists.")

    # Create directories
    dirs = [
        base,
        base / "models",
        base / "views",
        base / "security",
        base / "controllers",
        base / "static" / "description",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # __manifest__.py
    manifest = f"""\
{{
    "name": "{module_name}",
    "version": "1.0.0",
    "summary": "",
    "description": "",
    "author": "",
    "website": "",
    "category": "Uncategorized",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}}
"""
    _write(base / "__manifest__.py", manifest)

    # __init__.py (root)
    _write(base / "__init__.py", "from . import models\nfrom . import controllers\n")

    # models/__init__.py
    _write(base / "models" / "__init__.py", "from . import models\n")

    # models/models.py
    models_py = f"""\
from odoo import models, fields, api


class {_to_class_name(module_name)}(models.Model):
    _name = "{module_name.replace("_", ".")}"
    _description = "{module_name}"

    name = fields.Char(string="Name", required=True)
"""
    _write(base / "models" / "models.py", models_py)

    # views/views.xml
    views_xml = f"""\
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>

        <!-- {module_name} views -->

    </data>
</odoo>
"""
    _write(base / "views" / "views.xml", views_xml)

    # security/ir.model.access.csv
    _write(
        base / "security" / "ir.model.access.csv",
        "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n",
    )

    # controllers/__init__.py
    _write(base / "controllers" / "__init__.py", "from . import controllers\n")

    # controllers/controllers.py
    controllers_py = """\
# from odoo import http
# from odoo.http import request


# class MyController(http.Controller):
#     @http.route('/my_route', auth='public', type='http')
#     def index(self, **kw):
#         return "Hello, world!"
"""
    _write(base / "controllers" / "controllers.py", controllers_py)

    # static/description/icon.png placeholder
    _write(base / "static" / "description" / ".gitkeep", "")

    return str(base)


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _to_class_name(module_name: str) -> str:
    """Convert a_module_name to AModuleName."""
    return "".join(part.capitalize() for part in module_name.split("_"))
