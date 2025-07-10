"""
DataLab Core Platform - Núcleo Central da Plataforma Unificada
Integra todos os componentes em uma arquitetura coesa e escalável
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

try:
    import requests
except ImportError:
    requests = None

# Configurar logging centralizado
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class ServiceStatus(Enum):
    """Status dos serviços da plataforma"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """Informações de um serviço"""

    name: str
    version: str
    status: ServiceStatus
    endpoint: str
    port: int
    health_check_url: str
    dependencies: List[str]
    metrics: Dict[str, Any]
    last_check: datetime


@dataclass
class DataPipelineConfig:
    """Configuração de pipeline de dados"""

    name: str
    source: str
    destination: str
    transformation_type: str
    schedule: str
    enabled: bool
    parameters: Dict[str, Any]


class DataLabCore:
    """
    Núcleo central da plataforma DataLab
    Gerencia todos os serviços e componentes de forma unificada
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.services: Dict[str, ServiceInfo] = {}
        self.pipelines: Dict[str, DataPipelineConfig] = {}
        self.config = self._load_config()
        self._initialize_services()

    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração central da plataforma"""
        default_config = {
            "environment": os.getenv("DATALAB_ENVIRONMENT", "development"),
            "version": os.getenv("DATALAB_VERSION", "2.0.0"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "services": {
                "spark": {
                    "enabled": True,
                    "endpoint": "spark-master",
                    "port": 8080,
                    "health_path": "/",
                    "dependencies": ["minio"],
                },
                "minio": {
                    "enabled": True,
                    "endpoint": "minio",
                    "port": 9000,
                    "health_path": "/minio/health/live",
                    "dependencies": [],
                },
                "kafka": {
                    "enabled": True,
                    "endpoint": "kafka",
                    "port": 9092,
                    "health_path": None,
                    "dependencies": [],
                },
                "prefect": {
                    "enabled": True,
                    "endpoint": "prefect-server",
                    "port": 4200,
                    "health_path": "/api/health",
                    "dependencies": ["minio"],
                },
                "mlflow": {
                    "enabled": True,
                    "endpoint": "mlflow",
                    "port": 5000,
                    "health_path": "/health",
                    "dependencies": ["minio"],
                },
                "streamlit": {
                    "enabled": True,
                    "endpoint": "streamlit",
                    "port": 8501,
                    "health_path": "/_stcore/health",
                    "dependencies": ["prefect", "mlflow"],
                },
                "jupyterhub": {
                    "enabled": True,
                    "endpoint": "jupyterhub",
                    "port": 8000,
                    "health_path": "/hub/health",
                    "dependencies": ["spark", "minio"],
                },
            },
            "data_sources": {
                "bronze_bucket": "s3a://bronze",
                "silver_bucket": "s3a://silver",
                "gold_bucket": "s3a://gold",
                "mlflow_bucket": "s3a://mlflow",
                "backup_bucket": "s3a://backup",
            },
            "quality_thresholds": {
                "min_rows": 1000,
                "max_null_percentage": 5.0,
                "max_duplicate_percentage": 2.0,
                "min_quality_score": 0.85,
            },
        }

        # Tentar carregar configuração personalizada
        config_path = "/opt/datalab/config/platform.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    custom_config = json.load(f)
                    default_config.update(custom_config)
            except Exception as e:
                self.logger.warning(f"Erro ao carregar config personalizada: {e}")

        return default_config

    def _initialize_services(self):
        """Inicializa informações dos serviços"""
        for service_name, config in self.config["services"].items():
            if config["enabled"]:
                self.services[service_name] = ServiceInfo(
                    name=service_name,
                    version="unknown",
                    status=ServiceStatus.UNKNOWN,
                    endpoint=config["endpoint"],
                    port=config["port"],
                    health_check_url=f"http://{config['endpoint']}:{config['port']}{config.get('health_path', '')}",
                    dependencies=config.get("dependencies", []),
                    metrics={},
                    last_check=datetime.now(),
                )

    async def check_service_health(self, service_name: str) -> ServiceStatus:
        """Verifica saúde de um serviço específico"""
        if service_name not in self.services:
            return ServiceStatus.UNKNOWN

        service = self.services[service_name]

        try:
            try:
                import aiohttp

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        service.health_check_url,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as response:
                        if response.status < 400:
                            service.status = ServiceStatus.HEALTHY
                            service.last_check = datetime.now()
                            return ServiceStatus.HEALTHY
                        else:
                            service.status = ServiceStatus.DEGRADED
                            return ServiceStatus.DEGRADED
            except ImportError:
                # Fallback usando requests síncronos
                import requests

                response = requests.get(service.health_check_url, timeout=10)
                if response.status_code < 400:
                    service.status = ServiceStatus.HEALTHY
                    service.last_check = datetime.now()
                    return ServiceStatus.HEALTHY
                else:
                    service.status = ServiceStatus.DEGRADED
                    return ServiceStatus.DEGRADED

        except Exception as e:
            self.logger.warning(f"Health check falhou para {service_name}: {e}")
            service.status = ServiceStatus.UNHEALTHY
            return ServiceStatus.UNHEALTHY

    async def check_all_services_health(self) -> Dict[str, ServiceStatus]:
        """Verifica saúde de todos os serviços"""
        health_status = {}

        tasks = [
            self.check_service_health(service_name)
            for service_name in self.services.keys()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for service_name, result in zip(self.services.keys(), results):
            if isinstance(result, Exception):
                health_status[service_name] = ServiceStatus.UNHEALTHY
            else:
                health_status[service_name] = result

        return health_status

    def get_platform_status(self) -> Dict[str, Any]:
        """Retorna status geral da plataforma"""
        healthy_services = sum(
            1
            for service in self.services.values()
            if service.status == ServiceStatus.HEALTHY
        )
        total_services = len(self.services)

        platform_health = "healthy"
        if healthy_services == 0:
            platform_health = "critical"
        elif healthy_services < total_services * 0.8:
            platform_health = "degraded"

        return {
            "platform_health": platform_health,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "services": {
                name: {
                    "status": service.status.value,
                    "endpoint": service.endpoint,
                    "port": service.port,
                    "last_check": service.last_check.isoformat(),
                }
                for name, service in self.services.items()
            },
            "environment": self.config["environment"],
            "version": self.config["version"],
            "timestamp": datetime.now().isoformat(),
        }

    def register_pipeline(self, pipeline_config: DataPipelineConfig):
        """Registra um novo pipeline de dados"""
        self.pipelines[pipeline_config.name] = pipeline_config
        self.logger.info(f"Pipeline registrado: {pipeline_config.name}")

    def get_pipelines_status(self) -> Dict[str, Any]:
        """Retorna status de todos os pipelines"""
        return {
            "total_pipelines": len(self.pipelines),
            "enabled_pipelines": sum(1 for p in self.pipelines.values() if p.enabled),
            "pipelines": {
                name: {
                    "enabled": pipeline.enabled,
                    "source": pipeline.source,
                    "destination": pipeline.destination,
                    "schedule": pipeline.schedule,
                }
                for name, pipeline in self.pipelines.items()
            },
        }

    def get_service_dependencies(self, service_name: str) -> List[str]:
        """Retorna dependências de um serviço"""
        if service_name in self.services:
            return self.services[service_name].dependencies
        return []

    def get_startup_order(self) -> List[str]:
        """Calcula ordem de inicialização dos serviços baseada em dependências"""
        startup_order = []
        remaining_services = set(self.services.keys())

        while remaining_services:
            # Encontrar serviços sem dependências não resolvidas
            ready_services = []
            for service in remaining_services:
                dependencies = self.get_service_dependencies(service)
                if all(
                    dep in startup_order or dep not in self.services
                    for dep in dependencies
                ):
                    ready_services.append(service)

            if not ready_services:
                # Evitar loop infinito - adicionar serviços restantes
                ready_services = list(remaining_services)

            startup_order.extend(ready_services)
            remaining_services -= set(ready_services)

        return startup_order

    def get_unified_metrics(self) -> Dict[str, Any]:
        """Coleta métricas unificadas da plataforma"""
        return {
            "platform": self.get_platform_status(),
            "pipelines": self.get_pipelines_status(),
            "data_quality": {
                "thresholds": self.config["quality_thresholds"],
                "last_check": datetime.now().isoformat(),
            },
            "resources": {"data_sources": self.config["data_sources"]},
        }


# Instância global da plataforma
datalab_core = DataLabCore()


# Decorador para registrar automaticamente pipelines
def register_datalab_pipeline(
    name: str,
    source: str,
    destination: str,
    transformation_type: str = "etl",
    schedule: str = "daily",
    enabled: bool = True,
    **parameters,
):
    """Decorador para registrar pipelines automaticamente"""

    def decorator(func):
        pipeline_config = DataPipelineConfig(
            name=name,
            source=source,
            destination=destination,
            transformation_type=transformation_type,
            schedule=schedule,
            enabled=enabled,
            parameters=parameters,
        )
        datalab_core.register_pipeline(pipeline_config)
        return func

    return decorator


# Utilitários para integração
class DataLabIntegration:
    """Utilitários para integração com a plataforma"""

    @staticmethod
    def get_service_url(service_name: str) -> str:
        """Retorna URL completa de um serviço"""
        if service_name in datalab_core.services:
            service = datalab_core.services[service_name]
            return f"http://{service.endpoint}:{service.port}"
        raise ValueError(f"Serviço {service_name} não encontrado")

    @staticmethod
    def get_data_source_path(source_type: str) -> str:
        """Retorna caminho de uma fonte de dados"""
        data_sources = datalab_core.config["data_sources"]
        if f"{source_type}_bucket" in data_sources:
            return data_sources[f"{source_type}_bucket"]
        raise ValueError(f"Fonte de dados {source_type} não encontrada")

    @staticmethod
    def is_service_healthy(service_name: str) -> bool:
        """Verifica se um serviço está saudável"""
        if service_name in datalab_core.services:
            return datalab_core.services[service_name].status == ServiceStatus.HEALTHY
        return False

    @staticmethod
    def wait_for_services(services: List[str], timeout: int = 300) -> bool:
        """Aguarda serviços ficarem saudáveis"""
        import time

        start_time = time.time()

        while time.time() - start_time < timeout:
            if all(
                DataLabIntegration.is_service_healthy(service) for service in services
            ):
                return True
            time.sleep(10)

        return False


if __name__ == "__main__":
    # Exemplo de uso
    async def main():
        print("🚀 Inicializando DataLab Core Platform...")

        # Verificar saúde dos serviços
        health_status = await datalab_core.check_all_services_health()
        print("📊 Status dos serviços:")
        for service, status in health_status.items():
            print(f"   {service}: {status.value}")

        # Mostrar métricas unificadas
        metrics = datalab_core.get_unified_metrics()
        print(f"\n📈 Métricas da plataforma:")
        print(f"   Saúde geral: {metrics['platform']['platform_health']}")
        print(
            f"   Serviços saudáveis: {metrics['platform']['healthy_services']}/{metrics['platform']['total_services']}"
        )

        # Ordem de inicialização
        startup_order = datalab_core.get_startup_order()
        print(f"\n🔄 Ordem de inicialização recomendada: {' → '.join(startup_order)}")

    asyncio.run(main())
