import configparser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class OdooConfig:
    db_name: str
    addons_path: str
    config_path: Path

    @property
    def config_path_str(self) -> str:
        return str(self.config_path)


def find_config() -> Path:
    """Locate odoo.conf in the current working directory."""
    cwd = Path.cwd()
    conf = cwd / "odoo.conf"
    if conf.is_file():
        return conf
    raise FileNotFoundError(
        f"No odoo.conf found in {cwd}. "
        "Run this command from a directory containing odoo.conf, "
        "or pass --config explicitly."
    )


def parse_config(path: Path) -> OdooConfig:
    """Read an odoo.conf file and return an OdooConfig."""
    parser = configparser.ConfigParser()
    parser.read(path)

    options = parser["options"] if parser.has_section("options") else {}

    db_name = options.get("db_name", "")
    # Odoo writes "False" as the default — treat it as empty
    if db_name in ("False", "false", "None", "none"):
        db_name = ""

    return OdooConfig(
        db_name=db_name,
        addons_path=options.get("addons_path", ""),
        config_path=path,
    )


def resolve_config(
    config_path: Optional[str] = None,
    database: Optional[str] = None,
) -> OdooConfig:
    """Find and parse config, optionally overriding the database name."""
    path = Path(config_path) if config_path else find_config()
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")

    config = parse_config(path)

    if database:
        config.db_name = database

    if not config.db_name:
        raise ValueError(
            "No database name found in odoo.conf and none provided via --database. "
            "Please specify one."
        )

    return config
