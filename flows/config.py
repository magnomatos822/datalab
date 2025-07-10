"""
Configurações centralizadas para os fluxos Prefect do DataLab
"""

import os
from typing import Any, Dict

# Configurações de ambiente
ENVIRONMENT = os.getenv("DATALAB_ENVIRONMENT", "development")
VERSION = os.getenv("DATALAB_VERSION", "1.0.0")

# URLs dos serviços
SPARK_MASTER_URL = os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")

# Credenciais
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")

# Configurações de bucket S3
BUCKETS = {
    "bronze": "s3a://bronze",
    "silver": "s3a://silver",
    "gold": "s3a://gold",
    "mlflow": "s3a://mlflow",
    "prefect": "s3a://prefect",
    "backup": "s3a://backup",
}

# Configurações de retenção
RETENTION_POLICIES = {
    "bronze": 90,  # dias
    "silver": 60,  # dias
    "gold": 365,  # dias
    "logs": 30,  # dias
    "backups": 180,  # dias
}

# Configurações de qualidade de dados
DATA_QUALITY_THRESHOLDS = {
    "min_rows": 1000,
    "max_null_percentage": 5.0,
    "max_duplicate_percentage": 2.0,
    "min_quality_score": 0.85,
}

# Configurações de alertas
ALERT_SETTINGS = {
    "email_enabled": True,
    "slack_enabled": False,
    "webhook_url": None,
    "max_duration_minutes": 30,
    "max_consecutive_failures": 3,
}

# Configurações de recursos
RESOURCE_LIMITS = {
    "etl_flows": {"cpu_cores": 2, "memory_gb": 4, "timeout_minutes": 60},
    "mlops_flows": {"cpu_cores": 4, "memory_gb": 8, "timeout_minutes": 120},
    "monitoring_flows": {"cpu_cores": 1, "memory_gb": 1, "timeout_minutes": 10},
}

# Tópicos Kafka
KAFKA_TOPICS = {
    "events": "datalab-events",
    "notifications": "datalab-notifications",
    "metrics": "datalab-metrics",
    "alerts": "datalab-alerts",
}

# Tags padrão para flows
DEFAULT_TAGS = {"environment": ENVIRONMENT, "version": VERSION, "managed_by": "datalab"}


def get_spark_config() -> Dict[str, Any]:
    """Retorna configuração do Spark para os flows"""
    return {
        "spark.master": SPARK_MASTER_URL,
        "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        "spark.hadoop.fs.s3a.endpoint": MINIO_ENDPOINT,
        "spark.hadoop.fs.s3a.access.key": AWS_ACCESS_KEY_ID,
        "spark.hadoop.fs.s3a.secret.key": AWS_SECRET_ACCESS_KEY,
        "spark.hadoop.fs.s3a.path.style.access": "true",
        "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
        "spark.hadoop.fs.s3a.connection.maximum": 100,
        "spark.hadoop.fs.s3a.connection.timeout": 300000,
        "spark.hadoop.fs.s3a.attempts.maximum": 20,
        "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
    }


def get_mlflow_config() -> Dict[str, str]:
    """Retorna configuração do MLflow"""
    return {
        "MLFLOW_TRACKING_URI": MLFLOW_TRACKING_URI,
        "MLFLOW_S3_ENDPOINT_URL": MINIO_ENDPOINT,
        "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
    }


def get_kafka_config() -> Dict[str, Any]:
    """Retorna configuração do Kafka"""
    return {
        "bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
        "auto_offset_reset": "latest",
        "enable_auto_commit": True,
        "group_id": "datalab-flows",
    }
