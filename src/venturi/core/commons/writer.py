from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal

from ...config import PROJECT_ROOT
from ..spark import on_databricks
from .options import CsvWriteOptions, DeltaWriteOptions, Options

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, DataFrameWriter

    from ..model.table_model import TableModel

WriteMode = Literal["append", "overwrite", "error", "ignore"]


class Writer(ABC):
    format: str

    def __init__(self, options: Options, mode: WriteMode = "append", partition_by: list[str] | None = None):
        self.options = options
        self.mode = mode
        self.partition_by = partition_by or []

    def _writer(self, df: DataFrame) -> DataFrameWriter:
        writer = df.write.format(self.format).mode(self.mode).options(**self.options.to_spark())
        if self.partition_by:
            writer = writer.partitionBy(*self.partition_by)
        return writer

    @abstractmethod
    def write(self, df: DataFrame) -> None: ...


class DeltaWriter(Writer):
    format = "delta"

    def __init__(
        self,
        table_name: str,
        mode: WriteMode = "append",
        options: DeltaWriteOptions | None = None,
        partition_by: list[str] | None = None,
        table_path: str | None = None,
    ):
        """table_path : emplacement des données ; None laisse le catalogue le gérer."""
        super().__init__(options or DeltaWriteOptions(), mode, partition_by)
        self.table_name = table_name
        self.table_path = table_path

    def write(self, df: DataFrame) -> None:
        writer = self._writer(df)
        if self.table_path is not None:
            writer = writer.option("path", self.table_path)
        writer.saveAsTable(self.table_name)


class CsvWriter(Writer):
    format = "csv"

    def __init__(
        self,
        file_path: str,
        mode: WriteMode = "append",
        options: CsvWriteOptions | None = None,
        partition_by: list[str] | None = None,
    ):
        super().__init__(options or CsvWriteOptions(), mode, partition_by)
        self.file_path = file_path

    def write(self, df: DataFrame) -> None:
        self._writer(df).save(self.file_path)



def write_table(df: DataFrame, table: TableModel, mode: WriteMode = "append") -> None:
    """Écrit `df` dans une table de `tables.yaml`, en créant son schéma au besoin.

    Sur Databricks, la table est managée par Unity Catalog sous `full_table_name`.
    En local, Spark ne connaît pas le catalogue : la table est `<schéma>.<table>`,
    stockée à `table_path`.
    """
    if on_databricks():
        name, path = table.full_table_name, None
    else:
        name, path = f"{table.schema_name}.{table.table_name}", str(PROJECT_ROOT / table.table_path)

    df.sparkSession.sql(f"CREATE SCHEMA IF NOT EXISTS {name.rsplit('.', 1)[0]}")
    DeltaWriter(name, mode, table_path=path).write(df)
