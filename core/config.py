"""
Sistema de Configuração Unificado do DataLab
Centraliza todas as configurações da plataforma
"""

import json
import os

try:
    import yaml
except ImportError:
    yaml = None
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class Environment(Enum):
    """Ambientes disponíveis"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class ServiceConfig:
    """Configuração de um serviço"""

    name: str
    enabled: bool
    image: str
    version: str
    ports: Dict[str, int]
    environment: Dict[str, str]
    volumes: Dict[str, str]
    depends_on: list
    health_check: Dict[str, Any]
    resources: Dict[str, Any]


@dataclass
class DataSourceConfig:
    """Configuração de fonte de dados"""

    name: str
    type: str  # s3, database, api, file
    connection_string: str
    credentials: Dict[str, str]
    schema: Optional[Dict[str, Any]] = None


@dataclass
class PipelineConfig:
    """Configuração de pipeline"""

    name: str
    description: str
    schedule: str
    enabled: bool
    source: str
    destination: str
    transformations: list
    quality_checks: Dict[str, Any]
    notifications: Dict[str, Any]


class DataLabConfig:
    """
    Gerenciador de configuração central do DataLab
    """

    def __init__(self, config_dir: Optional[str] = None):
        """Inicializa o gerenciador de configuração com fallback de caminhos"""
        if config_dir is None:
            # Tentar diferentes caminhos
            possible_paths = [
                "/opt/datalab/config",
                "./config",
                "config",
                os.path.join(os.path.dirname(__file__), "..", "config"),
            ]

            for path in possible_paths:
                if os.path.exists(path) and os.access(path, os.R_OK):
                    config_dir = path
                    break
            else:
                # Se nenhum caminho for encontrado, usa o diretório atual
                config_dir = "./config"

        self.config_dir = Path(config_dir)
        # Criar apenas se tiver permissão
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # Se não conseguir criar, usa diretório local
            self.config_dir = Path("./config")
            self.config_dir.mkdir(parents=True, exist_ok=True)

        self.environment = Environment(os.getenv("DATALAB_ENVIRONMENT", "development"))
        self.version = os.getenv("DATALAB_VERSION", "2.0.0")

        self._base_config = self._load_base_config()
        self._env_config = self._load_environment_config()
        self._user_config = self._load_user_config()

        # Configuração final mesclada
        self.config = self._merge_configs()

    def _load_base_config(self) -> Dict[str, Any]:
        """Carrega configuração base da plataforma"""
        return {
            "platform": {
                "name": "DataLab",
                "version": self.version,
                "environment": self.environment.value,
                "debug": os.getenv("DEBUG", "false").lower() == "true",
                "log_level": os.getenv("LOG_LEVEL", "INFO"),
                "timezone": "America/Sao_Paulo",
            },
            "security": {
                "enable_auth": True,
                "jwt_secret": os.getenv("JWT_SECRET", "datalab-secret-key"),
                "session_timeout": 3600,
                "cors_origins": ["http://localhost:*"],
                "ssl_enabled": False,
            },
            "storage": {
                "default_backend": "minio",
                "retention_policy": {
                    "bronze": "90d",
                    "silver": "365d",
                    "gold": "7y",
                    "logs": "30d",
                    "backups": "1y",
                },
                "compression": {"enabled": True, "algorithm": "gzip", "level": 6},
            },
            "networking": {
                "internal_network": "dataflow-network",
                "service_discovery": {"enabled": True, "backend": "consul"},
                "load_balancer": {"enabled": False, "type": "nginx"},
            },
            "monitoring": {
                "metrics": {
                    "enabled": True,
                    "backend": "prometheus",
                    "scrape_interval": "15s",
                },
                "logging": {
                    "enabled": True,
                    "backend": "elasticsearch",
                    "retention": "30d",
                },
                "alerting": {
                    "enabled": True,
                    "channels": ["email", "slack"],
                    "thresholds": {
                        "cpu_usage": 80,
                        "memory_usage": 85,
                        "disk_usage": 90,
                        "error_rate": 5,
                    },
                },
            },
            "data_quality": {
                "enabled": True,
                "default_rules": {
                    "min_rows": 1000,
                    "max_null_percentage": 5.0,
                    "max_duplicate_percentage": 2.0,
                    "schema_evolution": True,
                },
                "validation_level": "strict",
            },
        }

    def _load_environment_config(self) -> Dict[str, Any]:
        """Carrega configuração específica do ambiente"""
        env_file = self.config_dir / f"{self.environment.value}.yaml"

        if env_file.exists():
            with open(env_file, "r") as f:
                if yaml:
                    return yaml.safe_load(f) or {}
                else:
                    return json.load(f) if f.name.endswith(".json") else {}

        # Configurações padrão por ambiente
        env_defaults = {
            Environment.DEVELOPMENT: {
                "platform": {"debug": True, "log_level": "DEBUG"},
                "security": {"enable_auth": False},
                "monitoring": {"metrics": {"enabled": False}},
                "resources": {"default_limits": {"cpu": "1", "memory": "2Gi"}},
            },
            Environment.STAGING: {
                "platform": {"debug": False, "log_level": "INFO"},
                "security": {"enable_auth": True},
                "monitoring": {"metrics": {"enabled": True}},
                "resources": {"default_limits": {"cpu": "2", "memory": "4Gi"}},
            },
            Environment.PRODUCTION: {
                "platform": {"debug": False, "log_level": "WARNING"},
                "security": {"enable_auth": True, "ssl_enabled": True},
                "monitoring": {
                    "metrics": {"enabled": True},
                    "alerting": {"enabled": True},
                },
                "resources": {"default_limits": {"cpu": "4", "memory": "8Gi"}},
            },
        }

        return env_defaults.get(self.environment, {})

    def _load_user_config(self) -> Dict[str, Any]:
        """Carrega configuração personalizada do usuário"""
        user_file = self.config_dir / "user.yaml"

        if user_file.exists():
            with open(user_file, "r") as f:
                if yaml:
                    return yaml.safe_load(f) or {}
                else:
                    return json.load(f) if f.name.endswith(".json") else {}

        return {}

    def _merge_configs(self) -> Dict[str, Any]:
        """Mescla todas as configurações em ordem de prioridade"""

        def deep_merge(base: dict, update: dict) -> dict:
            """Merge recursivo de dicionários"""
            for key, value in update.items():
                if (
                    key in base
                    and isinstance(base[key], dict)
                    and isinstance(value, dict)
                ):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        config = self._base_config.copy()
        deep_merge(config, self._env_config)
        deep_merge(config, self._user_config)

        return config

    def get_service_config(self, service_name: str) -> ServiceConfig:
        """Retorna configuração de um serviço específico"""
        services_config = {
            "minio": ServiceConfig(
                name="minio",
                enabled=True,
                image="bitnami/minio:latest",
                version="RELEASE.2025-04-22T22-12-26Z",
                ports={"api": 9000, "console": 9001},
                environment={
                    "MINIO_ROOT_USER": os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
                    "MINIO_ROOT_PASSWORD": os.getenv(
                        "AWS_SECRET_ACCESS_KEY", "minioadmin"
                    ),
                    "MINIO_DEFAULT_BUCKETS": "bronze,silver,gold,mlflow,prefect,backup",
                },
                volumes={
                    "data": "/bitnami/minio/data",
                    "config": "/docker-entrypoint-initdb.d",
                },
                depends_on=[],
                health_check={
                    "test": [
                        "CMD",
                        "curl",
                        "-f",
                        "http://localhost:9000/minio/health/live",
                    ],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                },
                resources=self.config.get("resources", {}).get("default_limits", {}),
            ),
            "kafka": ServiceConfig(
                name="kafka",
                enabled=True,
                image="bitnami/kafka:latest",
                version="7.5.0",
                ports={"internal": 9092, "external": 29092},
                environment={
                    "KAFKA_CFG_NODE_ID": "0",
                    "KAFKA_CFG_PROCESS_ROLES": "controller,broker",
                    "KAFKA_CFG_LISTENERS": "PLAINTEXT://:9092,CONTROLLER://:9093,EXTERNAL://:29092",
                    "KAFKA_CFG_ADVERTISED_LISTENERS": "PLAINTEXT://kafka:9092,EXTERNAL://localhost:29092",
                    "KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE": "true",
                },
                volumes={"data": "/bitnami/kafka"},
                depends_on=[],
                health_check={
                    "test": [
                        "CMD",
                        "kafka-topics.sh",
                        "--bootstrap-server",
                        "localhost:9092",
                        "--list",
                    ],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 5,
                },
                resources=self.config.get("resources", {}).get("default_limits", {}),
            ),
            "spark-master": ServiceConfig(
                name="spark-master",
                enabled=True,
                image="bitnami/spark:latest",
                version="3.5.1",
                ports={"ui": 8080, "master": 7077},
                environment={
                    "SPARK_MODE": "master",
                    "SPARK_RPC_AUTHENTICATION_ENABLED": "no",
                    "SPARK_RPC_ENCRYPTION_ENABLED": "no",
                    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
                    "AWS_SECRET_ACCESS_KEY": os.getenv(
                        "AWS_SECRET_ACCESS_KEY", "minioadmin"
                    ),
                },
                volumes={
                    "apps": "/opt/spark-apps",
                    "jars": "/opt/bitnami/spark/jars/custom",
                },
                depends_on=["minio"],
                health_check={
                    "test": ["CMD", "curl", "-f", "http://localhost:8080"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                },
                resources=self.config.get("resources", {}).get("default_limits", {}),
            ),
            "prefect-server": ServiceConfig(
                name="prefect-server",
                enabled=True,
                image="prefecthq/prefect:3.4.1-python3.11",
                version="3.4.1",
                ports={"api": 4200},
                environment={
                    "PREFECT_SERVER_API_HOST": "0.0.0.0",
                    "PREFECT_API_URL": "http://localhost:4200/api",
                    "PREFECT_UI_API_URL": "http://localhost:4200/api",
                    "PREFECT_SERVER_DATABASE_URL": "sqlite+aiosqlite:////opt/prefect/prefect.db",
                    "PREFECT_HOME": "/opt/prefect",
                },
                volumes={"data": "/opt/prefect", "flows": "/opt/prefect/flows"},
                depends_on=["minio", "kafka"],
                health_check={
                    "test": ["CMD", "curl", "-f", "http://localhost:4200/api/health"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 5,
                },
                resources=self.config.get("resources", {}).get("default_limits", {}),
            ),
            "mlflow": ServiceConfig(
                name="mlflow",
                enabled=True,
                image="datalab/mlflow:latest",
                version="2.22.0",
                ports={"ui": 5000},
                environment={
                    "MLFLOW_S3_ENDPOINT_URL": "http://minio:9000",
                    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
                    "AWS_SECRET_ACCESS_KEY": os.getenv(
                        "AWS_SECRET_ACCESS_KEY", "minioadmin"
                    ),
                },
                volumes={"config": "/opt/minio-config"},
                depends_on=["minio"],
                health_check={
                    "test": ["CMD", "curl", "-f", "http://localhost:5000"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                },
                resources=self.config.get("resources", {}).get("default_limits", {}),
            ),
            "streamlit": ServiceConfig(
                name="streamlit",
                enabled=True,
                image="datalab/streamlit:latest",
                version="1.45.0",
                ports={"web": 8501},
                environment={
                    "PREFECT_API_URL": "http://prefect-server:4200/api",
                    "MLFLOW_TRACKING_URI": "http://mlflow:5000",
                },
                volumes={"app": "/app"},
                depends_on=["prefect-server", "mlflow"],
                health_check={
                    "test": [
                        "CMD",
                        "curl",
                        "-f",
                        "http://localhost:8501/_stcore/health",
                    ],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                },
                resources=self.config.get("resources", {}).get("default_limits", {}),
            ),
        }

        if service_name not in services_config:
            raise ValueError(
                f"Configuração não encontrada para o serviço: {service_name}"
            )

        return services_config[service_name]

    def get_data_source_config(self, source_name: str) -> DataSourceConfig:
        """Retorna configuração de uma fonte de dados"""
        data_sources = {
            "bronze": DataSourceConfig(
                name="bronze",
                type="s3",
                connection_string="s3a://bronze",
                credentials={
                    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
                    "aws_secret_access_key": os.getenv(
                        "AWS_SECRET_ACCESS_KEY", "minioadmin"
                    ),
                    "endpoint_url": "http://minio:9000",
                },
            ),
            "silver": DataSourceConfig(
                name="silver",
                type="s3",
                connection_string="s3a://silver",
                credentials={
                    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
                    "aws_secret_access_key": os.getenv(
                        "AWS_SECRET_ACCESS_KEY", "minioadmin"
                    ),
                    "endpoint_url": "http://minio:9000",
                },
            ),
            "gold": DataSourceConfig(
                name="gold",
                type="s3",
                connection_string="s3a://gold",
                credentials={
                    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
                    "aws_secret_access_key": os.getenv(
                        "AWS_SECRET_ACCESS_KEY", "minioadmin"
                    ),
                    "endpoint_url": "http://minio:9000",
                },
            ),
        }

        if source_name not in data_sources:
            raise ValueError(f"Fonte de dados não encontrada: {source_name}")

        return data_sources[source_name]

    def get_pipeline_config(self, pipeline_name: str) -> PipelineConfig:
        """Retorna configuração de um pipeline"""
        pipelines = {
            "medallion_etl": PipelineConfig(
                name="medallion_etl",
                description="Pipeline ETL completo da arquitetura Medallion",
                schedule="0 6 * * *",  # Diário às 06:00
                enabled=True,
                source="bronze",
                destination="gold",
                transformations=[
                    "data_quality_check",
                    "silver_processing",
                    "gold_aggregation",
                ],
                quality_checks={
                    "min_rows": self.config["data_quality"]["default_rules"][
                        "min_rows"
                    ],
                    "max_null_percentage": self.config["data_quality"]["default_rules"][
                        "max_null_percentage"
                    ],
                },
                notifications={
                    "on_success": ["kafka"],
                    "on_failure": ["email", "slack"],
                },
            ),
            "realtime_monitoring": PipelineConfig(
                name="realtime_monitoring",
                description="Monitoramento em tempo real da plataforma",
                schedule="*/5 * * * *",  # A cada 5 minutos
                enabled=True,
                source="system",
                destination="metrics",
                transformations=["health_check", "metrics_collection"],
                quality_checks={},
                notifications={"on_failure": ["email"]},
            ),
        }

        if pipeline_name not in pipelines:
            raise ValueError(f"Pipeline não encontrado: {pipeline_name}")

        return pipelines[pipeline_name]

    def save_config(self, config_type: str = "user"):
        """Salva configuração atual em arquivo"""
        if config_type == "user":
            config_file = self.config_dir / "user.yaml"
            with open(config_file, "w") as f:
                if yaml:
                    yaml.dump(self._user_config, f, default_flow_style=False)
                else:
                    json.dump(self._user_config, f, indent=2)
        elif config_type == "environment":
            config_file = self.config_dir / f"{self.environment.value}.yaml"
            with open(config_file, "w") as f:
                if yaml:
                    yaml.dump(self._env_config, f, default_flow_style=False)
                else:
                    json.dump(self._env_config, f, indent=2)

    def update_config(self, path: str, value: Any):
        """Atualiza um valor específico na configuração"""
        keys = path.split(".")
        config = self._user_config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value
        self.config = self._merge_configs()

    def get_config_value(self, path: str, default: Any = None) -> Any:
        """Obtém um valor específico da configuração"""
        keys = path.split(".")
        config = self.config

        try:
            for key in keys:
                config = config[key]
            return config
        except (KeyError, TypeError):
            return default

    def export_config(self, format: str = "yaml") -> str:
        """Exporta configuração completa"""
        if format.lower() == "json":
            return json.dumps(self.config, indent=2, default=str)
        elif format.lower() == "yaml":
            if yaml:
                return yaml.dump(self.config, default_flow_style=False)
            else:
                return json.dumps(self.config, indent=2, default=str)
        else:
            raise ValueError("Formato suportado: 'json' ou 'yaml'")


# Instância global de configuração
datalab_config = DataLabConfig()


# Utilitários de acesso rápido
def get_service_config(service_name: str) -> ServiceConfig:
    """Acesso rápido à configuração de serviço"""
    return datalab_config.get_service_config(service_name)


def get_data_source_config(source_name: str) -> DataSourceConfig:
    """Acesso rápido à configuração de fonte de dados"""
    return datalab_config.get_data_source_config(source_name)


def get_config_value(path: str, default: Any = None) -> Any:
    """Acesso rápido a valores de configuração"""
    return datalab_config.get_config_value(path, default)
