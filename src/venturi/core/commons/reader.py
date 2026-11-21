from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ...config import PROJECT_ROOT
from ..spark import on_databricks
from .options import CsvReadOptions, DeltaReadOptions, Options

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, DataFrameReader, SparkSession
    from pyspark.sql.types import StructType

    from ..model.table_model import TableModel


class Reader(ABC):
    format: str

    def __init__(self, spark: SparkSession, options: Options):
        self.spark = spark
        self.options = options

    def _reader(self) -> DataFrameReader:
        return self.spark.read.format(self.format).options(**self.options.to_spark())

    @abstractmethod
    def read(self) -> DataFrame: ...


class DeltaReader(Reader):
    format = "delta"

    def __init__(
        self,
        spark: SparkSession,
        table_name: str,
        options: DeltaReadOptions | None = None,
        table_path: str | None = None,
    ):
        """table_path : lit les données à cet emplacement plutôt que par le catalogue."""
        super().__init__(spark, options or DeltaReadOptions())
        self.table_name = table_name
        self.table_path = table_path

    def read(self) -> DataFrame:
        if self.table_path is not None:
            return self._reader().load(self.table_path)
        return self._reader().table(self.table_name)


class CsvReader(Reader):
    format = "csv"

    def __init__(
        self,
        spark: SparkSession,
        file_path: str,
        options: CsvReadOptions | None = None,
        schema: StructType | None = None,
    ):
        super().__init__(spark, options or CsvReadOptions())
        self.file_path = file_path
        self.schema = schema

    def read(self) -> DataFrame:
        reader = self._reader()
        if self.schema is not None:
            reader = reader.schema(self.schema)
        return reader.load(self.file_path)


def read_table(spark: SparkSession, table: TableModel) -> DataFrame:
    """Lit une table de `tables.yaml`, symétrique de `write_table`.

    Sur Databricks, la table est lue par Unity Catalog sous `full_table_name`.
    En local, le catalogue de Spark est en mémoire et ne survit pas à la session :
    la table est lue à son emplacement, `table_path`.
    """
    if on_databricks():
        return DeltaReader(spark, table.full_table_name).read()
    return DeltaReader(spark, table.full_table_name, table_path=str(PROJECT_ROOT / table.table_path)).read()
