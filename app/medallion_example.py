"""
Exemplo de uso da arquitetura Medallion
"""

from medallion_architecture import MedallionArchitecture
from pyspark.sql.functions import avg, col, count, sum, window


def main():
    """Função principal com exemplo de uso da arquitetura Medallion"""

    # Cria a instância da arquitetura
    medallion = MedallionArchitecture()

    # Define o caminho para os dados de exemplo (CSV simulado)
    # Normalmente, esse seria um arquivo em um diretório compartilhado ou no MinIO
    sample_data_path = "/spark-apps/data/stocks.csv"

    # Função para transformar dados na camada Silver
    def silver_transform(df):
        """Aplica transformações para a camada Silver"""
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

    # Função para agregar dados na camada Gold
    def gold_transform(df):
        """Aplica transformações/agregações para a camada Gold"""
        # Calcula médias diárias
        daily_avg = df.groupBy("symbol", "date").agg(
            avg("close").alias("avg_close"), sum("volume").alias("total_volume")
        )

        # Adiciona métricas calculadas
        daily_avg = daily_avg.withColumn(
            "volume_price_ratio", col("total_volume") / col("avg_close")
        )

        return daily_avg

    try:
        # 1. Ingestão para Bronze
        bronze_path = medallion.ingest_to_bronze(
            source_path=sample_data_path,
            table_name="stocks_raw",
            format="csv",
            options={"header": "true", "inferSchema": "true"},
        )

        # 2. Processamento para Silver
        silver_path = medallion.process_to_silver(
            bronze_table="stocks_raw",
            silver_table="stocks_cleaned",
            transform_func=silver_transform,
        )

        # 3. Agregação para Gold
        gold_path = medallion.aggregate_to_gold(
            silver_table="stocks_cleaned",
            gold_table="stocks_daily_metrics",
            transform_func=gold_transform,
        )

        # 4. Demonstração de Time Travel (acessando versão anterior)
        try:
            # Tentando acessar versão 0 (inicial)
            historical_df = medallion.time_travel(
                layer="silver", table="stocks_cleaned", version=0
            )
            print(f"Contagem de registros na versão inicial: {historical_df.count()}")
        except Exception as e:
            print(f"Erro no Time Travel: {e}")

        print("Pipeline de dados completo!")

    except Exception as e:
        print(f"Erro no pipeline: {e}")


if __name__ == "__main__":
    main()
