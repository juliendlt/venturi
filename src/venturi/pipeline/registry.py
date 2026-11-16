"""Registre des pipelines exécutables depuis le point d'entrée.

Pour rendre un pipeline exécutable : l'ajouter à la liste ci-dessous.
"""

from .base import Pipeline
from .bronze.wind_farm import BronzeWindFarm
from .bronze.wind_turbine import BronzeWindTurbine

_PIPELINES: list[type[Pipeline]] = [
    BronzeWindFarm,
    BronzeWindTurbine,
]


def _build_registry(pipelines: list[type[Pipeline]]) -> dict[str, type[Pipeline]]:
    registry: dict[str, type[Pipeline]] = {}
    for pipeline in pipelines:
        if pipeline.name in registry:
            raise ValueError(f"Nom de pipeline en double : {pipeline.name!r}")
        registry[pipeline.name] = pipeline
    return registry


PIPELINES = _build_registry(_PIPELINES)
