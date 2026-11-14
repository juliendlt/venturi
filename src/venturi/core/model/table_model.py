from pydantic import BaseModel, ConfigDict, field_validator


class TableModel(BaseModel):
    full_table_name: str
    table_path: str
    version: int
    write_checkpoint: str | None = None

    @field_validator("full_table_name")
    @classmethod
    def check_schema_table_name(cls, value: str) -> str:
        parts = value.split(".")
        if len(parts) != 3 or not all(parts):
            raise ValueError(f"attendu <catalogue>.<schéma>.<table>, reçu {value!r}")
        return value

    @property
    def catalog_name(self) -> str:
        """Retourne le nom du catalogue """
        return self.full_table_name.split(".")[0]

    @property
    def schema_name(self) -> str:
        """Retourne le nom du schéma """
        return self.full_table_name.split(".")[1]

    @property
    def table_name(self) -> str:
        """Retourne le nom de la table """
        return self.full_table_name.split(".")[2]


class TablesModel(BaseModel):
    """Tables par zone. Une zone inconnue dans le YAML lève une erreur."""

    model_config = ConfigDict(extra="forbid")

    bronze: dict[str, TableModel] = {}
    silver: dict[str, TableModel] = {}
    gold: dict[str, TableModel] = {}
