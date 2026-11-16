import os

from pyspark.sql import SparkSession


def on_databricks() -> bool:
    return "DATABRICKS_RUNTIME_VERSION" in os.environ


def build_spark(app_name: str) -> SparkSession:
    """Session Spark : celle de Databricks si elle existe, sinon Spark local avec Delta."""
    if on_databricks():
        return SparkSession.builder.appName(app_name).getOrCreate()

    from delta import configure_spark_with_delta_pip

    builder = (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    )
    return configure_spark_with_delta_pip(builder).getOrCreate()
