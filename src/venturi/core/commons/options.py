"""Options de lecture et d'écriture Spark, typées par format.

Chaque classe est immuable (équivalent d'une case class). Les champs sont en
snake_case et convertis vers le nom d'option Spark en camelCase :
`infer_schema` -> `inferSchema`. Un champ à None n'est pas transmis à Spark, qui
applique alors sa valeur par défaut.
"""

from dataclasses import asdict, dataclass


def _to_camel_case(name: str) -> str:
    first, *others = name.split("_")
    return first + "".join(word.capitalize() for word in others)


@dataclass(frozen=True)
class Options:
    def to_spark(self) -> dict[str, str]:
        """Retourne les options au format attendu par Spark."""
        return {
            _to_camel_case(name): str(value).lower() if isinstance(value, bool) else str(value)
            for name, value in asdict(self).items()
            if value is not None
        }


# --- Lecture ---------------------------------------------------------------


@dataclass(frozen=True)
class CsvReadOptions(Options):
    header: bool = True
    sep: str = ","
    encoding: str = "UTF-8"
    quote: str = '"'
    escape: str = '"'
    multi_line: bool = False
    infer_schema: bool = False
    null_value: str | None = None
    date_format: str | None = None
    timestamp_format: str | None = None
    # FAILFAST : une ligne malformée fait échouer la lecture au lieu d'être
    # silencieusement remplacée par des null (PERMISSIVE, défaut de Spark).
    mode: str = "FAILFAST"


@dataclass(frozen=True)
class DeltaReadOptions(Options):
    # Time travel : au plus un des deux.
    version_as_of: int | None = None
    timestamp_as_of: str | None = None

    def __post_init__(self) -> None:
        if self.version_as_of is not None and self.timestamp_as_of is not None:
            raise ValueError("version_as_of et timestamp_as_of sont exclusifs")


# --- Écriture --------------------------------------------------------------


@dataclass(frozen=True)
class CsvWriteOptions(Options):
    header: bool = True
    sep: str = ","
    encoding: str = "UTF-8"
    quote: str = '"'
    escape: str = '"'
    null_value: str | None = None
    date_format: str | None = None
    timestamp_format: str | None = None
    compression: str | None = None



@dataclass(frozen=True)
class DeltaWriteOptions(Options):
    # merge_schema : accepte l'ajout de colonnes. overwrite_schema : remplace le
    # schéma (mode overwrite). replace_where : n'écrase que les lignes du prédicat.
    merge_schema: bool = False
    overwrite_schema: bool = False
    replace_where: str | None = None
