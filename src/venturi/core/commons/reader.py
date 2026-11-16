from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .options import CsvReadOptions, DeltaReadOptions, Options

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, DataFrameReader, SparkSession
    from pyspark.sql.types import StructType


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

    def __init__(self, spark: SparkSession, table_name: str, options: DeltaReadOptions | None = None):
        super().__init__(spark, options or DeltaReadOptions())
        self.table_name = table_name

    def read(self) -> DataFrame:
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


