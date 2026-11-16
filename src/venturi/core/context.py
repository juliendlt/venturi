from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .model.landing_model import LandingsModel
from .model.table_model import TablesModel

if TYPE_CHECKING:
    from pyspark.sql import SparkSession


@dataclass(frozen=True)
class Context:
    """Tout ce dont un pipeline a besoin pour s'exécuter. Créé par le point d'entrée."""

    spark: SparkSession
    tables: TablesModel
    landing: LandingsModel
    logger: logging.Logger
    project_root: Path
