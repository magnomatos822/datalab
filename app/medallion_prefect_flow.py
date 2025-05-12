"""
Orquestração do pipeline Medallion utilizando Prefect
"""

import datetime

from medallion_architecture import MedallionArchitecture
from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner
from pyspark.sql.functions import avg, col, count, sum, window


@task(name="Ingest to Bronze Layer")
def ingest_to_bronze_task(source_path, table_name, format="csv", options=None):
    """Task para ingerir dados na camada Bronze"""
    medallion = MedallionArchitecture()
    bronze_path = medallion.ingest_to_bronze(source_path, table_name, format, options)
    return bronze_path


@task(name="Process to Silver Layer")
def process_to_silver_task(bronze_table, silver_table):
    """Task para processar dados para a camada Silver"""

    def silver_transform(df):
        """Transformações para a camada Silver"""
        # Converte tipos de dados
        df = (
            df.withColumn("close", col("close").cast("double"))
            .withColumn("volume", col("volume").cast("double"))
            .withColumn("date", col("date").cast("date"))
        )

        # Filtra dados inválidos
        df = df.filter(col("close").isNotNull())
        df = df.filter(col("volume") > 0)

        return df

    medallion = MedallionArchitecture()
    silver_path = medallion.process_to_silver(
        bronze_table, silver_table, silver_transform
    )
    return silver_path


@task(name="Aggregate to Gold Layer")
def aggregate_to_gold_task(silver_table, gold_table):
    """Task para agregar dados para a camada Gold"""

    def gold_transform(df):
        """Transformações/agregações para a camada Gold"""
        # Calcula médias diárias
        daily_avg = df.groupBy("symbol", "date").agg(
            avg("close").alias("avg_close"), sum("volume").alias("total_volume")
        )

        # Adiciona métricas calculadas
        daily_avg = daily_avg.withColumn(
            "volume_price_ratio", col("total_volume") / col("avg_close")
        )

        return daily_avg

    medallion = MedallionArchitecture()
    gold_path = medallion.aggregate_to_gold(silver_table, gold_table, gold_transform)
    return gold_path


@flow(
    name="Medallion Architecture Pipeline",
    description="Pipeline completo da arquitetura Medallion",
    task_runner=SequentialTaskRunner(),
)
def medallion_pipeline(source_path="/spark-apps/data/stocks.csv"):
    """
    Fluxo Prefect completo para processar dados através da arquitetura Medallion

    Args:
        source_path: Caminho para os dados de origem
    """
    # Adiciona timestamp para evitar conflitos de nome
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Parâmetros da ingestão
    bronze_table = f"stocks_raw_{timestamp}"
    silver_table = f"stocks_cleaned_{timestamp}"
    gold_table = f"stocks_metrics_{timestamp}"

    # Executa as tasks em sequência, passando o resultado de uma para a próxima
    bronze_path = ingest_to_bronze_task(source_path, bronze_table)
    silver_path = process_to_silver_task(bronze_table, silver_table)
    gold_path = aggregate_to_gold_task(silver_table, gold_table)

    return {
        "bronze_path": bronze_path,
        "silver_path": silver_path,
        "gold_path": gold_path,
        "bronze_table": bronze_table,
        "silver_table": silver_table,
        "gold_table": gold_table,
    }


if __name__ == "__main__":
    # Execução direta do fluxo para teste
    result = medallion_pipeline()
    print(f"Pipeline concluído! Resultados: {result}")
