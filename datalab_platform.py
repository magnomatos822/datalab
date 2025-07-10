#!/usr/bin/env python3
"""
DataLab Unified Platform - Plataforma Unificada de Dados
Sistema integrado completo para processamento, análise e ML

Este é o ponto de entrada principal da plataforma DataLab.
Integra todos os componentes em uma arquitetura coesa e escalável.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Adicionar diretórios ao path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "core"))
sys.path.insert(0, str(Path(__file__).parent / "flows"))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/datalab.log")],
)

logger = logging.getLogger(__name__)


class DataLabPlatform:
    """
    Plataforma Unificada DataLab
    Orquestra todos os componentes do ecossistema de dados
    """

    def __init__(self, config_path: Optional[str] = None):
        """Inicializa a plataforma DataLab"""
        self.config_path = config_path or "config/platform.yaml"
        self.core_platform = None
        self.orchestrator = None
        self.config = None

        # Status da plataforma
        self.is_initialized = False
        self.running_services = []

    async def initialize(self):
        """Inicializa todos os componentes da plataforma"""
        logger.info("🚀 Inicializando DataLab Platform...")

        try:
            # 1. Inicializar configuração
            await self._initialize_config()

            # 2. Inicializar plataforma core
            await self._initialize_core_platform()

            # 3. Inicializar orquestrador
            await self._initialize_orchestrator()

            # 4. Registrar pipelines padrão
            await self._register_default_pipelines()

            # 5. Verificar saúde dos serviços
            await self._perform_health_checks()

            self.is_initialized = True
            logger.info("✅ DataLab Platform inicializada com sucesso!")

        except Exception as e:
            logger.error(f"❌ Falha na inicialização da plataforma: {e}")
            raise

    async def _initialize_config(self):
        """Inicializa sistema de configuração"""
        try:
            from core.config import DataLabConfig

            self.config = DataLabConfig()
            logger.info("✅ Sistema de configuração inicializado")
        except ImportError as e:
            logger.warning(f"⚠️ Sistema de configuração não disponível: {e}")
            self.config = None

    async def _initialize_core_platform(self):
        """Inicializa plataforma core"""
        try:
            from core.platform import DataLabCore

            self.core_platform = DataLabCore()

            # Registrar serviços principais
            await self._register_core_services()

            logger.info("✅ Plataforma core inicializada")
        except ImportError as e:
            logger.warning(f"⚠️ Plataforma core não disponível: {e}")
            self.core_platform = None

    async def _initialize_orchestrator(self):
        """Inicializa orquestrador unificado"""
        try:
            from core.orchestrator import UnifiedOrchestrator

            self.orchestrator = UnifiedOrchestrator()
            logger.info("✅ Orquestrador unificado inicializado")
        except ImportError as e:
            logger.warning(f"⚠️ Orquestrador não disponível: {e}")
            self.orchestrator = None

    async def _register_core_services(self):
        """Registra serviços principais da plataforma"""
        if not self.core_platform:
            return

        services = [
            {
                "name": "prefect-server",
                "type": "orchestration",
                "endpoint": "http://localhost:4200",
                "health_check": "http://localhost:4200/api/health",
                "port": 4200,
            },
            {
                "name": "spark-master",
                "type": "compute",
                "endpoint": "http://localhost:8080",
                "health_check": "http://localhost:8080",
                "port": 8080,
            },
            {
                "name": "minio",
                "type": "storage",
                "endpoint": "http://localhost:9000",
                "health_check": "http://localhost:9000/minio/health/live",
                "port": 9000,
            },
            {
                "name": "mlflow",
                "type": "ml_tracking",
                "endpoint": "http://localhost:5000",
                "health_check": "http://localhost:5000/health",
                "port": 5000,
            },
            {
                "name": "streamlit",
                "type": "dashboard",
                "endpoint": "http://localhost:8501",
                "health_check": "http://localhost:8501/healthz",
                "port": 8501,
            },
            {
                "name": "jupyterhub",
                "type": "notebook",
                "endpoint": "http://localhost:8000",
                "health_check": "http://localhost:8000/hub/health",
                "port": 8000,
            },
        ]

        for service_config in services:
            await self.core_platform.register_service(
                service_config["name"], service_config
            )

    async def _register_default_pipelines(self):
        """Registra pipelines padrão da plataforma"""
        if not self.orchestrator:
            return

        # Pipeline ETL Medallion
        self.orchestrator.register_pipeline(
            "medallion_etl",
            ["bronze_ingestion", "silver_processing", "gold_aggregation"],
            schedule="0 6 * * *",  # Diário às 6h
            enabled=True,
        )

        # Pipeline de Monitoramento
        self.orchestrator.register_pipeline(
            "monitoring",
            ["health_check", "metrics_collection", "alert_processing"],
            schedule="*/5 * * * *",  # A cada 5 minutos
            enabled=True,
        )

        # Pipeline MLOps
        self.orchestrator.register_pipeline(
            "mlops",
            ["model_training", "model_validation", "model_deployment"],
            schedule="0 2 * * 1",  # Semanalmente às 2h da segunda-feira
            enabled=True,
        )

        logger.info("✅ Pipelines padrão registrados")

    async def _perform_health_checks(self):
        """Realiza verificações de saúde iniciais"""
        if not self.core_platform:
            logger.warning("⚠️ Verificações de saúde não disponíveis")
            return

        try:
            health_status = await self.core_platform.check_all_services_health()

            healthy_services = [
                service
                for service, status in health_status.items()
                if str(status) == "ServiceStatus.HEALTHY"
            ]

            self.running_services = healthy_services

            logger.info(f"✅ Serviços saudáveis: {len(healthy_services)}")
            logger.info(f"📊 Status dos serviços: {health_status}")

        except Exception as e:
            logger.warning(f"⚠️ Erro nas verificações de saúde: {e}")

    async def start_services(self, services: Optional[List[str]] = None):
        """Inicia serviços específicos ou todos"""
        logger.info("🔄 Iniciando serviços...")

        # TODO: Implementar inicialização real dos serviços via Docker Compose
        # Por enquanto, apenas log
        services_to_start = services or [
            "prefect-server",
            "spark-master",
            "minio",
            "mlflow",
            "streamlit",
            "jupyterhub",
        ]

        for service in services_to_start:
            logger.info(f"▶️ Iniciando {service}...")
            # Aqui seria feita a chamada real para Docker Compose
            # subprocess.run(["docker-compose", "up", "-d", service])

        logger.info("✅ Serviços iniciados!")

    async def stop_services(self, services: Optional[List[str]] = None):
        """Para serviços específicos ou todos"""
        logger.info("🛑 Parando serviços...")

        services_to_stop = services or self.running_services

        for service in services_to_stop:
            logger.info(f"⏹️ Parando {service}...")
            # subprocess.run(["docker-compose", "stop", service])

        logger.info("✅ Serviços parados!")

    async def execute_pipeline(
        self, pipeline_name: str, parameters: Optional[Dict] = None
    ):
        """Executa um pipeline específico"""
        if not self.orchestrator:
            logger.error("❌ Orquestrador não disponível")
            return None

        logger.info(f"🚀 Executando pipeline: {pipeline_name}")

        try:
            execution = await self.orchestrator.execute_pipeline(
                pipeline_name, parameters
            )
            logger.info(f"✅ Pipeline {pipeline_name} executado: {execution.id}")
            return execution
        except Exception as e:
            logger.error(f"❌ Erro na execução do pipeline {pipeline_name}: {e}")
            raise

    async def get_platform_status(self) -> Dict[str, Any]:
        """Retorna status completo da plataforma"""
        status = {
            "platform": {
                "initialized": self.is_initialized,
                "running_services": len(self.running_services),
                "total_services": 6,  # Número de serviços core
            },
            "components": {
                "core_platform": self.core_platform is not None,
                "orchestrator": self.orchestrator is not None,
                "config": self.config is not None,
            },
        }

        # Adicionar status do orquestrador se disponível
        if self.orchestrator:
            orchestrator_status = await self.orchestrator.get_status()
            status["orchestrator"] = orchestrator_status

        # Adicionar status da plataforma core se disponível
        if self.core_platform:
            platform_status = self.core_platform.get_platform_status()
            status["platform"].update(platform_status)

        return status

    async def shutdown(self):
        """Desliga a plataforma graciosamente"""
        logger.info("🔄 Desligando DataLab Platform...")

        # Parar pipelines ativos
        if self.orchestrator:
            await self.orchestrator.stop_all_pipelines()

        # Parar serviços
        await self.stop_services()

        logger.info("✅ DataLab Platform desligada com sucesso!")


# CLI para controle da plataforma
async def main():
    """Função principal da CLI"""
    parser = argparse.ArgumentParser(description="DataLab Unified Platform")
    parser.add_argument(
        "command",
        choices=["init", "start", "stop", "status", "pipeline", "health"],
        help="Comando a executar",
    )
    parser.add_argument("--service", help="Serviço específico")
    parser.add_argument("--pipeline", help="Pipeline específico")
    parser.add_argument("--config", help="Arquivo de configuração")

    args = parser.parse_args()

    # Criar instância da plataforma
    platform = DataLabPlatform(config_path=args.config)

    try:
        if args.command == "init":
            await platform.initialize()

        elif args.command == "start":
            await platform.initialize()
            services = [args.service] if args.service else None
            await platform.start_services(services)

        elif args.command == "stop":
            services = [args.service] if args.service else None
            await platform.stop_services(services)

        elif args.command == "status":
            await platform.initialize()
            status = await platform.get_platform_status()
            print("📊 Status da Plataforma DataLab:")
            print(f"   Inicializada: {status['platform']['initialized']}")
            print(f"   Serviços Ativos: {status['platform']['running_services']}")
            print(f"   Componentes: {status['components']}")

        elif args.command == "pipeline":
            if not args.pipeline:
                print("❌ Especifique um pipeline com --pipeline")
                return
            await platform.initialize()
            await platform.execute_pipeline(args.pipeline)

        elif args.command == "health":
            await platform.initialize()
            await platform._perform_health_checks()

    except KeyboardInterrupt:
        logger.info("🛑 Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
    finally:
        await platform.shutdown()


if __name__ == "__main__":
    # Criar diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)

    # Executar plataforma
    asyncio.run(main())
