"""
Implementação de exemplo da arquitetura Medallion com Delta Lake
"""

import logging
import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, lit
from tenacity import retry, stop_after_attempt, wait_exponential

# Configurações
BRONZE_BUCKET = os.environ.get("MINIO_BUCKET_BRONZE", "s3a://bronze")
SILVER_BUCKET = os.environ.get("MINIO_BUCKET_SILVER", "s3a://silver")
GOLD_BUCKET = os.environ.get("MINIO_BUCKET_GOLD", "s3a://gold")

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
def create_spark_session():
    """Cria uma sessão Spark com suporte a Delta Lake com retry para resiliência"""
    logger.info("Inicializando sessão Spark com suporte a Delta Lake")

    # Obter credenciais do ambiente (mais seguro)
    access_key = os.environ.get("AWS_ACCESS_KEY_ID", "admin")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "admin123")
    endpoint = os.environ.get("MINIO_ENDPOINT", "http://minio:9000")

    return (
        SparkSession.builder.appName("MedallionArchitecture")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.hadoop.fs.s3a.endpoint", endpoint)
        .config("spark.hadoop.fs.s3a.access.key", access_key)
        .config("spark.hadoop.fs.s3a.secret.key", secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        # Configurações para melhorar resiliência
        .config("spark.hadoop.fs.s3a.connection.maximum", 100)
        .config("spark.hadoop.fs.s3a.connection.timeout", 300000)
        .config("spark.hadoop.fs.s3a.attempts.maximum", 20)
        .config("spark.hadoop.fs.s3a.retry.interval", "1s")
        .config("spark.hadoop.fs.s3a.retry.limit", 20)
        .getOrCreate()
    )


class MedallionArchitecture:
    """Classe que implementa a arquitetura medallion (Bronze, Silver, Gold)"""

    def __init__(self):
        self.spark = create_spark_session()

    def ingest_to_bronze(self, source_path, table_name, format="csv", options=None):
        """
        Ingere dados brutos para a camada Bronze

        Args:
            source_path: Caminho para os dados de origem
            table_name: Nome da tabela a ser criada
            format: Formato dos dados de origem (csv, json, parquet, etc)
            options: Opções adicionais para leitura
        """
        if options is None:
            options = {"header": "true", "inferSchema": "true"}

        print(f"Ingerindo dados de {source_path} para camada Bronze")

        # Lê os dados de origem
        df = self.spark.read.format(format).options(**options).load(source_path)

        # Adiciona metadados
        bronze_df = df.withColumn(
            "ingestion_timestamp", current_timestamp()
        ).withColumn("source", lit(source_path))

        # Salva na camada Bronze usando Delta
        bronze_path = os.path.join(BRONZE_BUCKET, table_name)

        bronze_df.write.format("delta").mode("overwrite").save(bronze_path)

        print(f"Dados salvos na camada Bronze: {bronze_path}")
        return bronze_path

    def process_to_silver(self, bronze_table, silver_table, transform_func=None):
        """
        Processa dados da camada Bronze para a camada Silver

        Args:
            bronze_table: Nome da tabela na camada Bronze
            silver_table: Nome da tabela na camada Silver
            transform_func: Função de transformação a ser aplicada (opcional)
        """
        print(f"Processando {bronze_table} para camada Silver")

        # Lê os dados da camada Bronze
        bronze_path = os.path.join(BRONZE_BUCKET, bronze_table)
        df = self.spark.read.format("delta").load(bronze_path)

        # Aplica transformações, se fornecidas
        if transform_func:
            df = transform_func(df)
        else:
            # Transformações padrão: remover nulos, renomear colunas, etc.
            # Apenas um exemplo simples aqui
            df = df.dropDuplicates()

        # Adiciona metadados
        silver_df = df.withColumn("processed_timestamp", current_timestamp())

        # Salva na camada Silver usando Delta
        silver_path = os.path.join(SILVER_BUCKET, silver_table)

        silver_df.write.format("delta").mode("overwrite").save(silver_path)

        print(f"Dados salvos na camada Silver: {silver_path}")
        return silver_path

    def aggregate_to_gold(self, silver_table, gold_table, transform_func):
        """
        Agrega dados da camada Silver para a camada Gold

        Args:
            silver_table: Nome da tabela na camada Silver
            gold_table: Nome da tabela na camada Gold
            transform_func: Função de agregação/transformação a ser aplicada
        """
        print(f"Agregando {silver_table} para camada Gold")

        # Lê os dados da camada Silver
        silver_path = os.path.join(SILVER_BUCKET, silver_table)
        df = self.spark.read.format("delta").load(silver_path)

        # Aplica transformações
        gold_df = transform_func(df)

        # Adiciona metadados
        gold_df = gold_df.withColumn("aggregated_timestamp", current_timestamp())

        # Salva na camada Gold usando Delta
        gold_path = os.path.join(GOLD_BUCKET, gold_table)

        gold_df.write.format("delta").mode("overwrite").save(gold_path)

        print(f"Dados salvos na camada Gold: {gold_path}")
        return gold_path

    def time_travel(self, layer, table, version=None, timestamp=None):
        """
        Acessa versões anteriores dos dados usando Time Travel do Delta Lake

        Args:
            layer: Camada (bronze, silver, gold)
            table: Nome da tabela
            version: Versão específica (opcional)
            timestamp: Timestamp específico (opcional)
        """
        bucket_map = {
            "bronze": BRONZE_BUCKET,
            "silver": SILVER_BUCKET,
            "gold": GOLD_BUCKET,
        }

        path = os.path.join(bucket_map[layer], table)

        if version is not None:
            df = (
                self.spark.read.format("delta")
                .option("versionAsOf", version)
                .load(path)
            )
            print(f"Acessando versão {version} da tabela {table}")
        elif timestamp is not None:
            df = (
                self.spark.read.format("delta")
                .option("timestampAsOf", timestamp)
                .load(path)
            )
            print(f"Acessando tabela {table} no timestamp {timestamp}")
        else:
            raise ValueError("Deve fornecer versão ou timestamp")

        return df
