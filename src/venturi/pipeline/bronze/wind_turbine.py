from ...core.commons.reader import CsvReader
from ...core.commons.writer import write_table
from ...core.context import Context
from ..base import Pipeline


class BronzeWindTurbine(Pipeline):
    name = "bronze.wind_turbine"
    description = "Registre OREOL des aérogénérateurs"

    landing_key = "wind_turbine"
    table_key = "wind_turbine"

    def run(self, context: Context) -> None:
        source = str(context.project_root / context.landing.oreol[self.landing_key].file_path)
        table = context.tables.bronze[self.table_key]

        context.logger.info("Lecture de %s", source)
        df = CsvReader(context.spark, source).read()

        context.logger.info("Écriture de %s", table.full_table_name)
        write_table(df, table, mode="overwrite")
