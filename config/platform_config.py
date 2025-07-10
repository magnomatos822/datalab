"""
DataLab Platform Configuration - Configuração Centralizada
Sistema de configuração unificado para toda a plataforma
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfiguration:
    """Configuração de um serviço"""

    name: str
    enabled: bool = True
    image: str = ""
    version: str = "latest"
    ports: Optional[Dict[str, int]] = None
    environment: Optional[Dict[str, str]] = None
    volumes: Optional[List[str]] = None
    health_check: str = ""
    dependencies: Optional[List[str]] = None
    resources: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.ports is None:
            self.ports = {}
        if self.environment is None:
            self.environment = {}
        if self.volumes is None:
            self.volumes = []
        if self.dependencies is None:
            self.dependencies = []
        if self.resources is None:
            self.resources = {}


@dataclass
class PipelineConfiguration:
    """Configuração de um pipeline"""

    name: str
    description: str = ""
    enabled: bool = True
    schedule: str = ""
    tasks: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    retry_policy: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []
        if self.parameters is None:
            self.parameters = {}
        if self.retry_policy is None:
            self.retry_policy = {"max_retries": 3, "delay": 60}
        if self.notifications is None:
            self.notifications = {}


class PlatformConfiguration:
    """
    Configuração Central da Plataforma DataLab
    Gerencia todas as configurações em um local centralizado
    """

    def __init__(self, config_dir: str = "config"):
        """Inicializa o sistema de configuração"""
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        # Configurações carregadas
        self._platform_config = {}
        self._services_config = {}
        self._pipelines_config = {}
        self._environment_config = {}

        # Carregar configurações
        self._load_configurations()

    def _load_configurations(self):
        """Carrega todas as configurações dos arquivos"""
        try:
            # Configuração da plataforma
            self._platform_config = self._load_config_file(
                "platform.yaml", self._default_platform_config()
            )

            # Configuração dos serviços
            self._services_config = self._load_config_file(
                "services.yaml", self._default_services_config()
            )

            # Configuração dos pipelines
            self._pipelines_config = self._load_config_file(
                "pipelines.yaml", self._default_pipelines_config()
            )

            # Configuração do ambiente
            env = os.getenv("DATALAB_ENV", "development")
            self._environment_config = self._load_config_file(f"env/{env}.yaml", {})

            logger.info("✅ Configurações carregadas com sucesso")

        except Exception as e:
            logger.error(f"❌ Erro ao carregar configurações: {e}")
            # Usar configurações padrão
            self._use_default_configurations()

    def _load_config_file(
        self, filename: str, default: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Carrega um arquivo de configuração específico"""
        file_path = self.config_dir / filename

        if not file_path.exists():
            logger.warning(
                f"⚠️ Arquivo {filename} não encontrado, usando configuração padrão"
            )
            self._save_config_file(filename, default)
            return default

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if filename.endswith(".yaml") or filename.endswith(".yml"):
                    if yaml:
                        return yaml.safe_load(f) or default
                    else:
                        logger.warning("PyYAML não disponível, tentando JSON")
                        return json.load(f)
                else:
                    return json.load(f)
        except Exception as e:
            logger.error(f"❌ Erro ao carregar {filename}: {e}")
            return default

    def _save_config_file(self, filename: str, config: Dict[str, Any]):
        """Salva um arquivo de configuração"""
        file_path = self.config_dir / filename
        file_path.parent.mkdir(exist_ok=True)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                if filename.endswith(".yaml") or filename.endswith(".yml"):
                    if yaml:
                        yaml.dump(
                            config, f, default_flow_style=False, allow_unicode=True
                        )
                    else:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar {filename}: {e}")

    def _use_default_configurations(self):
        """Usa configurações padrão quando há erro no carregamento"""
        self._platform_config = self._default_platform_config()
        self._services_config = self._default_services_config()
        self._pipelines_config = self._default_pipelines_config()
        self._environment_config = {}

    def _default_platform_config(self) -> Dict[str, Any]:
        """Configuração padrão da plataforma"""
        return {
            "platform": {
                "name": "DataLab",
                "version": "1.0.0",
                "environment": os.getenv("DATALAB_ENV", "development"),
                "debug": True,
                "log_level": "INFO",
            },
            "storage": {
                "data_lake": {
                    "provider": "minio",
                    "endpoint": "http://localhost:9000",
                    "access_key": "minio",
                    "secret_key": "minio123",
                    "buckets": {
                        "bronze": "bronze",
                        "silver": "silver",
                        "gold": "gold",
                        "mlflow": "mlflow",
                    },
                }
            },
            "compute": {
                "spark": {
                    "master": "spark://localhost:7077",
                    "app_name": "DataLab",
                    "executor_memory": "2g",
                    "driver_memory": "1g",
                }
            },
            "monitoring": {
                "metrics": {"enabled": True, "interval": 30},
                "alerts": {"enabled": True, "channels": ["log", "kafka"]},
            },
            "security": {
                "authentication": False,
                "authorization": False,
                "encryption": False,
            },
        }

    def _default_services_config(self) -> Dict[str, Any]:
        """Configuração padrão dos serviços"""
        return {
            "prefect": ServiceConfiguration(
                name="prefect-server",
                image="prefecthq/prefect:2.14.11-python3.11",
                ports={"api": 4200},
                environment={
                    "PREFECT_UI_URL": "http://localhost:4200",
                    "PREFECT_API_URL": "http://localhost:4200/api",
                    "PREFECT_SERVER_API_HOST": "0.0.0.0",
                },
                health_check="http://localhost:4200/api/health",
            ),
            "spark": ServiceConfiguration(
                name="spark-master",
                image="bitnami/spark:3.5",
                ports={"ui": 8080, "master": 7077},
                environment={
                    "SPARK_MODE": "master",
                    "SPARK_RPC_AUTHENTICATION_ENABLED": "no",
                    "SPARK_RPC_ENCRYPTION_ENABLED": "no",
                },
                health_check="http://localhost:8080",
            ),
            "minio": ServiceConfiguration(
                name="minio",
                image="minio/minio:latest",
                ports={"api": 9000, "console": 9001},
                environment={
                    "MINIO_ROOT_USER": "minio",
                    "MINIO_ROOT_PASSWORD": "minio123",
                },
                health_check="http://localhost:9000/minio/health/live",
            ),
            "mlflow": ServiceConfiguration(
                name="mlflow",
                image="python:3.11",
                ports={"ui": 5000},
                environment={
                    "MLFLOW_BACKEND_STORE_URI": "sqlite:///mlflow.db",
                    "MLFLOW_DEFAULT_ARTIFACT_ROOT": "s3://mlflow/artifacts",
                },
                health_check="http://localhost:5000/health",
            ),
            "streamlit": ServiceConfiguration(
                name="streamlit",
                image="python:3.11",
                ports={"ui": 8501},
                environment={
                    "STREAMLIT_SERVER_PORT": "8501",
                    "STREAMLIT_SERVER_ADDRESS": "0.0.0.0",
                },
                health_check="http://localhost:8501/healthz",
            ),
            "jupyterhub": ServiceConfiguration(
                name="jupyterhub",
                image="jupyterhub/jupyterhub:latest",
                ports={"ui": 8000},
                environment={
                    "JUPYTERHUB_CRYPT_KEY": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
                },
                health_check="http://localhost:8000/hub/health",
            ),
        }

    def _default_pipelines_config(self) -> Dict[str, Any]:
        """Configuração padrão dos pipelines"""
        return {
            "medallion_etl": PipelineConfiguration(
                name="medallion_etl",
                description="Pipeline ETL com arquitetura Medallion",
                schedule="0 6 * * *",  # Diário às 6h
                tasks=["bronze_ingestion", "silver_processing", "gold_aggregation"],
                parameters={
                    "source_path": "/data/raw/stocks.csv",
                    "enable_quality_checks": True,
                    "min_rows_threshold": 1000,
                },
                retry_policy={"max_retries": 3, "delay": 60},
                notifications={"on_failure": ["email", "slack"]},
            ),
            "monitoring": PipelineConfiguration(
                name="monitoring",
                description="Pipeline de monitoramento da plataforma",
                schedule="*/5 * * * *",  # A cada 5 minutos
                tasks=["health_check", "metrics_collection", "alert_processing"],
                parameters={"check_interval": 300},
                retry_policy={"max_retries": 2, "delay": 30},
            ),
            "mlops": PipelineConfiguration(
                name="mlops",
                description="Pipeline MLOps para treinamento e deploy",
                schedule="0 2 * * 1",  # Semanalmente às 2h
                tasks=["model_training", "model_validation", "model_deployment"],
                parameters={"model_type": "regression", "validation_threshold": 0.8},
                retry_policy={"max_retries": 1, "delay": 120},
            ),
            "maintenance": PipelineConfiguration(
                name="maintenance",
                description="Pipeline de manutenção e limpeza",
                schedule="0 1 * * 0",  # Semanalmente domingo à 1h
                tasks=["cleanup_logs", "optimize_storage", "backup_metadata"],
                parameters={"retention_days": 30},
            ),
        }

    # Métodos públicos para acessar configurações

    def get_platform_config(
        self, key: Optional[str] = None, default: Any = None
    ) -> Any:
        """Obtém configuração da plataforma"""
        if key is None:
            return self._platform_config

        keys = key.split(".")
        config = self._platform_config

        try:
            for k in keys:
                config = config[k]
            return config
        except (KeyError, TypeError):
            return default

    def get_service_config(self, service_name: str) -> Optional[ServiceConfiguration]:
        """Obtém configuração de um serviço"""
        service_data = self._services_config.get(service_name)
        if not service_data:
            return None

        if isinstance(service_data, ServiceConfiguration):
            return service_data
        else:
            return ServiceConfiguration(**service_data)

    def get_pipeline_config(
        self, pipeline_name: str
    ) -> Optional[PipelineConfiguration]:
        """Obtém configuração de um pipeline"""
        pipeline_data = self._pipelines_config.get(pipeline_name)
        if not pipeline_data:
            return None

        if isinstance(pipeline_data, PipelineConfiguration):
            return pipeline_data
        else:
            return PipelineConfiguration(**pipeline_data)

    def get_all_services(self) -> Dict[str, ServiceConfiguration]:
        """Obtém configuração de todos os serviços"""
        services = {}
        for name, config in self._services_config.items():
            if isinstance(config, ServiceConfiguration):
                services[name] = config
            else:
                services[name] = ServiceConfiguration(**config)
        return services

    def get_all_pipelines(self) -> Dict[str, PipelineConfiguration]:
        """Obtém configuração de todos os pipelines"""
        pipelines = {}
        for name, config in self._pipelines_config.items():
            if isinstance(config, PipelineConfiguration):
                pipelines[name] = config
            else:
                pipelines[name] = PipelineConfiguration(**config)
        return pipelines

    def update_config(self, section: str, key: str, value: Any):
        """Atualiza uma configuração específica"""
        config_map = {
            "platform": self._platform_config,
            "services": self._services_config,
            "pipelines": self._pipelines_config,
            "environment": self._environment_config,
        }

        if section not in config_map:
            raise ValueError(f"Seção inválida: {section}")

        config_map[section][key] = value

        # Salvar alteração
        filename_map = {
            "platform": "platform.yaml",
            "services": "services.yaml",
            "pipelines": "pipelines.yaml",
            "environment": f"env/{os.getenv('DATALAB_ENV', 'development')}.yaml",
        }

        self._save_config_file(filename_map[section], config_map[section])

    def export_config(self, format: str = "yaml") -> str:
        """Exporta toda a configuração"""
        full_config = {
            "platform": self._platform_config,
            "services": self._services_config,
            "pipelines": self._pipelines_config,
            "environment": self._environment_config,
        }

        if format.lower() == "json":
            return json.dumps(full_config, indent=2, default=str)
        elif format.lower() == "yaml":
            if yaml:
                return yaml.dump(full_config, default_flow_style=False)
            else:
                return json.dumps(full_config, indent=2, default=str)
        else:
            raise ValueError("Formato deve ser 'json' ou 'yaml'")

    def validate_configuration(self) -> Dict[str, List[str]]:
        """Valida todas as configurações"""
        errors = {"platform": [], "services": [], "pipelines": []}

        # Validar plataforma
        required_platform_keys = ["platform.name", "platform.version"]
        for key in required_platform_keys:
            if not self.get_platform_config(key):
                errors["platform"].append(f"Chave obrigatória ausente: {key}")

        # Validar serviços
        for service_name, service_config in self.get_all_services().items():
            if not service_config.name:
                errors["services"].append(f"Nome ausente para serviço: {service_name}")
            if not service_config.health_check:
                errors["services"].append(
                    f"Health check ausente para serviço: {service_name}"
                )

        # Validar pipelines
        for pipeline_name, pipeline_config in self.get_all_pipelines().items():
            if not pipeline_config.name:
                errors["pipelines"].append(
                    f"Nome ausente para pipeline: {pipeline_name}"
                )
            if not pipeline_config.tasks:
                errors["pipelines"].append(
                    f"Tasks ausentes para pipeline: {pipeline_name}"
                )

        return errors


# Instância global de configuração
platform_config = PlatformConfiguration()


# Funções de conveniência
def get_service_config(service_name: str) -> Optional[ServiceConfiguration]:
    """Função de conveniência para obter configuração de serviço"""
    return platform_config.get_service_config(service_name)


def get_pipeline_config(pipeline_name: str) -> Optional[PipelineConfiguration]:
    """Função de conveniência para obter configuração de pipeline"""
    return platform_config.get_pipeline_config(pipeline_name)


def get_platform_config(key: Optional[str] = None, default: Any = None) -> Any:
    """Função de conveniência para obter configuração da plataforma"""
    return platform_config.get_platform_config(key, default)
