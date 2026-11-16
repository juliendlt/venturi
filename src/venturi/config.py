from pathlib import Path
import yaml

from .core.model.landing_model import LandingsModel
from .core.model.table_model import TablesModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TABLES_CONFIG_PATH = PROJECT_ROOT / "config" / "tables.yaml"
LANDING_CONFIG_PATH = PROJECT_ROOT / "config" / "landing.yaml"


def load_tables(path: Path = TABLES_CONFIG_PATH) -> TablesModel:
    """Charge et valide les tables du YAML"""
    with open(path, encoding="utf-8") as f:
        zones = yaml.safe_load(f) or {}

    return TablesModel.model_validate(zones)


def load_landing(path: Path = LANDING_CONFIG_PATH) -> LandingsModel:
    """Charge et valide les paths de la landing du YAML"""
    with open(path, encoding="utf-8") as f:
        sources = yaml.safe_load(f) or {}

    return LandingsModel.model_validate(sources)