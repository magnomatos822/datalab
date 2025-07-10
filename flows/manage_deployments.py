"""
Script para gerenciar deployments do Prefect no DataLab
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List

# Adicionar o diretório flows ao path
sys.path.append(str(Path(__file__).parent))

from config import DEFAULT_TAGS, ENVIRONMENT, VERSION

try:
    from datetime import timedelta

    from maintenance_flow import data_lake_maintenance_flow

    # Importar os flows
    from medallion_etl_flow import medallion_etl_pipeline
    from mlops_flow import mlops_pipeline
    from monitoring_flow import realtime_monitoring_flow
    from prefect import get_client
    from prefect.client.schemas import FlowRun
    from prefect.deployments import Deployment
    from prefect.server.schemas.schedules import CronSchedule, IntervalSchedule

except ImportError as e:
    print(f"❌ Erro ao importar dependências: {e}")
    print("💡 Execute: pip install prefect==3.4.1")
    sys.exit(1)


class DataLabFlowManager:
    """Gerenciador de fluxos Prefect para o DataLab"""

    def __init__(self):
        self.deployments = []
        self._setup_deployments()

    def _setup_deployments(self):
        """Configura todos os deployments do DataLab"""

        # 1. ETL Medallion Pipeline (Diário)
        etl_deployment = Deployment.build_from_flow(
            flow=medallion_etl_pipeline,
            name="medallion-etl-daily",
            version=VERSION,
            schedule=CronSchedule(
                cron="0 6 * * *", timezone="America/Sao_Paulo"  # 06:00 todos os dias
            ),
            work_pool_name="default-agent-pool",
            tags=["etl", "medallion", "daily", "production"]
            + list(DEFAULT_TAGS.values()),
            parameters={
                "source_path": "/opt/spark-apps/data/stocks.csv",
                "enable_quality_checks": True,
                "min_rows_threshold": 1000,
            },
            description="Pipeline ETL diário com arquitetura Medallion (Bronze → Silver → Gold)",
        )

        # 2. Monitoramento em Tempo Real (A cada 5 minutos)
        monitoring_deployment = Deployment.build_from_flow(
            flow=realtime_monitoring_flow,
            name="datalab-monitoring-realtime",
            version=VERSION,
            schedule=IntervalSchedule(interval=timedelta(minutes=5)),
            work_pool_name="default-agent-pool",
            tags=["monitoring", "realtime", "health-check", "critical"]
            + list(DEFAULT_TAGS.values()),
            description="Monitoramento em tempo real da saúde da plataforma DataLab",
        )

        # 3. MLOps Pipeline (Semanal - Domingos)
        mlops_deployment = Deployment.build_from_flow(
            flow=mlops_pipeline,
            name="mlops-weekly-retrain",
            version=VERSION,
            schedule=CronSchedule(
                cron="0 2 * * 0", timezone="America/Sao_Paulo"  # 02:00 aos domingos
            ),
            work_pool_name="default-agent-pool",
            tags=["mlops", "training", "weekly", "ml"] + list(DEFAULT_TAGS.values()),
            parameters={
                "data_path": "s3://gold/stocks_analytics/latest",
                "model_type": "random_forest",
                "experiment_name": "datalab-stock-prediction",
            },
            description="Pipeline semanal de retreinamento de modelos ML",
        )

        # 4. Manutenção do Data Lake (Semanal - Sábados)
        maintenance_deployment = Deployment.build_from_flow(
            flow=data_lake_maintenance_flow,
            name="datalake-maintenance-weekly",
            version=VERSION,
            schedule=CronSchedule(
                cron="0 3 * * 6", timezone="America/Sao_Paulo"  # 03:00 aos sábados
            ),
            work_pool_name="default-agent-pool",
            tags=["maintenance", "cleanup", "weekly", "optimization"]
            + list(DEFAULT_TAGS.values()),
            parameters={"retention_days": 30},
            description="Manutenção semanal do Data Lake (limpeza, otimização, backup)",
        )

        # 5. ETL de Alta Frequência (Experimental - A cada hora)
        high_freq_etl_deployment = Deployment.build_from_flow(
            flow=medallion_etl_pipeline,
            name="medallion-etl-hourly",
            version=VERSION,
            schedule=CronSchedule(
                cron="0 * * * *", timezone="America/Sao_Paulo"  # A cada hora
            ),
            work_pool_name="default-agent-pool",
            tags=["etl", "medallion", "hourly", "experimental"]
            + list(DEFAULT_TAGS.values()),
            parameters={
                "source_path": "/opt/spark-apps/data/realtime_stocks.csv",
                "enable_quality_checks": False,  # Mais rápido para alta frequência
                "min_rows_threshold": 100,
            },
            description="Pipeline ETL experimental de alta frequência (experimental)",
            is_schedule_active=False,  # Inativo por padrão
        )

        self.deployments = [
            etl_deployment,
            monitoring_deployment,
            mlops_deployment,
            maintenance_deployment,
            high_freq_etl_deployment,
        ]

    async def deploy_all(self):
        """Faz deploy de todos os fluxos"""
        print("🚀 Fazendo deploy de todos os fluxos DataLab...")

        for deployment in self.deployments:
            try:
                await deployment.apply()
                print(f"✅ {deployment.name} - Deploy realizado com sucesso")
            except Exception as e:
                print(f"❌ {deployment.name} - Erro no deploy: {str(e)}")

    async def list_deployments(self):
        """Lista todos os deployments"""
        print("📋 Listando deployments ativos...")

        async with get_client() as client:
            deployments = await client.read_deployments()

            if not deployments:
                print("ℹ️ Nenhum deployment encontrado")
                return

            print(f"\n📊 Total de deployments: {len(deployments)}")
            print("-" * 80)

            for deployment in deployments:
                status = "🟢 Ativo" if deployment.is_schedule_active else "🔴 Inativo"
                schedule_info = "Sem agendamento"

                if deployment.schedule:
                    if hasattr(deployment.schedule, "cron"):
                        schedule_info = f"Cron: {deployment.schedule.cron}"
                    elif hasattr(deployment.schedule, "interval"):
                        schedule_info = f"Intervalo: {deployment.schedule.interval}"

                print(f"📝 {deployment.name}")
                print(f"   Status: {status}")
                print(f"   Agendamento: {schedule_info}")
                print(f"   Tags: {', '.join(deployment.tags or [])}")
                print(f"   Versão: {deployment.version}")
                print()

    async def trigger_flow(self, deployment_name: str):
        """Executa um fluxo manualmente"""
        print(f"▶️ Executando fluxo: {deployment_name}")

        async with get_client() as client:
            try:
                flow_run = await client.create_flow_run_from_deployment(
                    deployment_id=None, deployment_name=deployment_name
                )
                print(f"✅ Fluxo iniciado - ID: {flow_run.id}")
                return flow_run.id
            except Exception as e:
                print(f"❌ Erro ao executar fluxo: {str(e)}")
                return None

    async def get_recent_runs(self, limit: int = 10):
        """Obtém execuções recentes"""
        print(f"📈 Últimas {limit} execuções...")

        async with get_client() as client:
            flow_runs = await client.read_flow_runs(limit=limit)

            if not flow_runs:
                print("ℹ️ Nenhuma execução encontrada")
                return

            print("-" * 80)
            for run in flow_runs:
                status_emoji = {
                    "COMPLETED": "✅",
                    "FAILED": "❌",
                    "RUNNING": "🏃",
                    "PENDING": "⏳",
                    "CANCELLED": "🚫",
                }.get(str(run.state_type), "❓")

                print(f"{status_emoji} {run.name}")
                print(f"   Flow: {run.flow_name}")
                print(f"   Estado: {run.state_type}")
                print(f"   Início: {run.start_time}")
                if run.end_time:
                    duration = run.end_time - run.start_time
                    print(f"   Duração: {duration}")
                print()


async def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("📋 Uso: python manage_deployments.py <comando>")
        print("\nComandos disponíveis:")
        print("  deploy     - Faz deploy de todos os fluxos")
        print("  list       - Lista todos os deployments")
        print("  runs       - Mostra execuções recentes")
        print("  trigger <nome> - Executa um fluxo manualmente")
        return

    command = sys.argv[1]
    manager = DataLabFlowManager()

    if command == "deploy":
        await manager.deploy_all()

    elif command == "list":
        await manager.list_deployments()

    elif command == "runs":
        await manager.get_recent_runs()

    elif command == "trigger":
        if len(sys.argv) < 3:
            print("❌ Especifique o nome do deployment para executar")
            return
        deployment_name = sys.argv[2]
        await manager.trigger_flow(deployment_name)

    else:
        print(f"❌ Comando desconhecido: {command}")


if __name__ == "__main__":
    asyncio.run(main())
