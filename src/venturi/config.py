from pathlib import Path
import yaml

from .core.model.table_model import TablesModel

TABLES_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "tables.yaml"


def load_tables(path: Path = TABLES_CONFIG_PATH) -> TablesModel:
    """Charge et valide les tables du YAML"""
    with open(path, encoding="utf-8") as f:
        zones = yaml.safe_load(f) or {}

    return TablesModel.model_validate(zones)
