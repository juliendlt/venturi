from pydantic import BaseModel, ConfigDict, field_validator


class LandingModel(BaseModel):
    file_path: str


class LandingsModel(BaseModel):
    """Tables par zone. Une zone inconnue dans le YAML lève une erreur."""

    model_config = ConfigDict(extra="forbid")

    oreol: dict[str, LandingModel] = {}

