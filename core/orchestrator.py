"""
Sistema de Orquestração Unificado do DataLab
Integra Prefect, Spark, MLflow e todos os componentes em uma plataforma coesa
"""

import asyncio
import json
import logging
import os

# Adicionar caminhos de forma segura
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
possible_paths = ["/opt/datalab", project_root, "."]
for path in possible_paths:
    if path not in sys.path:
        sys.path.append(path)

try:
    from core.config import DataLabConfig, get_config_value, get_service_config
    from core.platform import DataLabCore, ServiceStatus, datalab_core
except ImportError:
    # Fallback para desenvolvimento
    DataLabCore = None
    ServiceStatus = None
    datalab_core = None
    DataLabConfig = None
    get_config_value = lambda x, y: y
    get_service_config = lambda x: {}


class OrchestrationStatus(Enum):
    """Status da orquestração"""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class TaskPriority(Enum):
    """Prioridade de tasks"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class UnifiedTask:
    """Task unificada da plataforma"""

    id: str
    name: str
    description: str
    function: Callable
    priority: TaskPriority
    dependencies: List[str]
    retry_count: int
    timeout_seconds: int
    resources: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class PipelineExecution:
    """Execução de pipeline"""

    id: str
    pipeline_name: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    tasks_completed: int
    tasks_total: int
    error_message: Optional[str]
    metrics: Dict[str, Any]


class UnifiedOrchestrator:
    """
    Orquestrador unificado que integra todos os componentes do DataLab
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.status = OrchestrationStatus.IDLE
        self.registered_pipelines: Dict[str, Any] = {}
        self.active_executions: Dict[str, PipelineExecution] = {}
        self.task_registry: Dict[str, UnifiedTask] = {}

        # Integrações
        self.core_platform = datalab_core
        self.config = DataLabConfig() if DataLabConfig else None

        # Inicializar componentes
        self._initialize_integrations()
        self._register_core_tasks()

    def _initialize_integrations(self):
        """Inicializa integrações com todos os componentes"""
        self.integrations = {
            "prefect": PrefectIntegration(),
            "spark": SparkIntegration(),
            "mlflow": MLflowIntegration(),
            "kafka": KafkaIntegration(),
            "monitoring": MonitoringIntegration(),
        }

        self.logger.info("🔗 Integrações inicializadas")

    def _register_core_tasks(self):
        """Registra tasks fundamentais da plataforma"""

        # Task de verificação de saúde
        self.register_task(
            UnifiedTask(
                id="health_check",
                name="Health Check",
                description="Verifica saúde de todos os serviços",
                function=self._health_check_task,
                priority=TaskPriority.HIGH,
                dependencies=[],
                retry_count=3,
                timeout_seconds=60,
                resources={"cpu": "100m", "memory": "128Mi"},
                metadata={"category": "monitoring"},
            )
        )

        # Task de sincronização de dados
        self.register_task(
            UnifiedTask(
                id="data_sync",
                name="Data Synchronization",
                description="Sincroniza dados entre camadas",
                function=self._data_sync_task,
                priority=TaskPriority.MEDIUM,
                dependencies=["health_check"],
                retry_count=5,
                timeout_seconds=300,
                resources={"cpu": "500m", "memory": "1Gi"},
                metadata={"category": "data"},
            )
        )

        # Task de qualidade de dados
        self.register_task(
            UnifiedTask(
                id="data_quality",
                name="Data Quality Check",
                description="Executa verificações de qualidade",
                function=self._data_quality_task,
                priority=TaskPriority.HIGH,
                dependencies=["data_sync"],
                retry_count=3,
                timeout_seconds=600,
                resources={"cpu": "1", "memory": "2Gi"},
                metadata={"category": "quality"},
            )
        )

        # Task de backup
        self.register_task(
            UnifiedTask(
                id="backup",
                name="Data Backup",
                description="Executa backup de dados críticos",
                function=self._backup_task,
                priority=TaskPriority.LOW,
                dependencies=[],
                retry_count=2,
                timeout_seconds=1800,
                resources={"cpu": "200m", "memory": "512Mi"},
                metadata={"category": "maintenance"},
            )
        )

    def register_task(self, task: UnifiedTask):
        """Registra uma nova task"""
        self.task_registry[task.id] = task
        self.logger.info(f"📝 Task registrada: {task.name}")

    def register_pipeline(
        self,
        name: str,
        tasks: List[str],
        schedule: Optional[str] = None,
        enabled: bool = True,
    ):
        """Registra um novo pipeline"""
        pipeline = {
            "name": name,
            "tasks": tasks,
            "schedule": schedule,
            "enabled": enabled,
            "created_at": datetime.now(),
            "last_run": None,
            "success_count": 0,
            "failure_count": 0,
        }

        self.registered_pipelines[name] = pipeline
        self.logger.info(f"🔄 Pipeline registrado: {name}")

    async def execute_pipeline(
        self, pipeline_name: str, parameters: Optional[Dict[str, Any]] = None
    ) -> PipelineExecution:
        """Executa um pipeline específico"""
        if pipeline_name not in self.registered_pipelines:
            raise ValueError(f"Pipeline não encontrado: {pipeline_name}")

        pipeline = self.registered_pipelines[pipeline_name]
        execution_id = f"{pipeline_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        execution = PipelineExecution(
            id=execution_id,
            pipeline_name=pipeline_name,
            status="running",
            start_time=datetime.now(),
            end_time=None,
            tasks_completed=0,
            tasks_total=len(pipeline["tasks"]),
            error_message=None,
            metrics={},
        )

        self.active_executions[execution_id] = execution

        try:
            self.logger.info(f"🚀 Iniciando execução: {execution_id}")

            # Executar tasks em ordem de dependências
            for task_id in pipeline["tasks"]:
                await self._execute_task(task_id, execution, parameters or {})
                execution.tasks_completed += 1

            execution.status = "completed"
            execution.end_time = datetime.now()
            pipeline["success_count"] += 1

            self.logger.info(f"✅ Execução concluída: {execution_id}")

        except Exception as e:
            execution.status = "failed"
            execution.end_time = datetime.now()
            execution.error_message = str(e)
            pipeline["failure_count"] += 1

            self.logger.error(f"❌ Execução falhou: {execution_id} - {e}")
            raise

        finally:
            pipeline["last_run"] = datetime.now()

        return execution

    async def _execute_task(
        self, task_id: str, execution: PipelineExecution, parameters: Dict[str, Any]
    ):
        """Executa uma task específica"""
        if task_id not in self.task_registry:
            raise ValueError(f"Task não encontrada: {task_id}")

        task = self.task_registry[task_id]

        self.logger.info(f"⚡ Executando task: {task.name}")

        # Verificar dependências
        for dep_id in task.dependencies:
            if dep_id not in execution.metrics or not execution.metrics[dep_id].get(
                "success", False
            ):
                raise RuntimeError(f"Dependência não satisfeita: {dep_id}")

        # Executar task com retry
        for attempt in range(task.retry_count + 1):
            try:
                start_time = datetime.now()
                result = await task.function(parameters)
                end_time = datetime.now()

                execution.metrics[task_id] = {
                    "success": True,
                    "duration_seconds": (end_time - start_time).total_seconds(),
                    "attempt": attempt + 1,
                    "result": result,
                }

                self.logger.info(f"✅ Task concluída: {task.name}")
                break

            except Exception as e:
                if attempt < task.retry_count:
                    self.logger.warning(
                        f"⚠️ Task falhou (tentativa {attempt + 1}): {task.name} - {e}"
                    )
                    await asyncio.sleep(2**attempt)  # Backoff exponencial
                else:
                    execution.metrics[task_id] = {
                        "success": False,
                        "error": str(e),
                        "attempt": attempt + 1,
                    }
                    raise

    async def _health_check_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Task de verificação de saúde"""
        if not self.core_platform:
            return {"status": "warning", "message": "Core platform not available"}

        health_status = await self.core_platform.check_all_services_health()

        unhealthy_services = [
            service
            for service, status in health_status.items()
            if status != (ServiceStatus.HEALTHY if ServiceStatus else "healthy")
        ]

        if unhealthy_services:
            self.logger.warning(f"⚠️ Serviços não saudáveis: {unhealthy_services}")

        return {
            "healthy_services": len(health_status) - len(unhealthy_services),
            "total_services": len(health_status),
            "unhealthy_services": unhealthy_services,
            "timestamp": datetime.now().isoformat(),
        }

    async def _data_sync_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Task de sincronização de dados"""
        # Integração com Spark para processamento
        spark_integration = self.integrations.get("spark")

        if spark_integration:
            result = await spark_integration.sync_data_layers()
            return {
                "layers_synced": result.get("layers_synced", 0),
                "records_processed": result.get("records_processed", 0),
                "sync_duration": result.get("duration_seconds", 0),
            }

        return {"status": "spark_not_available"}

    async def _data_quality_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Task de verificação de qualidade"""
        quality_thresholds = get_config_value("data_quality.default_rules", {})

        # Simular verificação de qualidade
        quality_score = 0.94  # Seria calculado baseado nos dados reais

        return {
            "quality_score": quality_score,
            "thresholds": quality_thresholds,
            "passed": quality_score
            >= quality_thresholds.get("min_quality_score", 0.85),
        }

    async def _backup_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Task de backup"""
        # Integração com sistema de backup
        backup_size_gb = 2.5  # Seria calculado baseado no backup real

        return {
            "backup_size_gb": backup_size_gb,
            "backup_location": "s3://backup/",
            "backup_timestamp": datetime.now().isoformat(),
        }

    def get_pipeline_status(self, pipeline_name: str) -> Dict[str, Any]:
        """Retorna status de um pipeline"""
        if pipeline_name not in self.registered_pipelines:
            return {"error": "Pipeline não encontrado"}

        pipeline = self.registered_pipelines[pipeline_name]
        active_executions = [
            exec
            for exec in self.active_executions.values()
            if exec.pipeline_name == pipeline_name and exec.status == "running"
        ]

        return {
            "name": pipeline["name"],
            "enabled": pipeline["enabled"],
            "schedule": pipeline["schedule"],
            "last_run": (
                pipeline["last_run"].isoformat() if pipeline["last_run"] else None
            ),
            "success_count": pipeline["success_count"],
            "failure_count": pipeline["failure_count"],
            "active_executions": len(active_executions),
            "task_count": len(pipeline["tasks"]),
        }

    def get_platform_metrics(self) -> Dict[str, Any]:
        """Retorna métricas unificadas da plataforma"""
        active_pipelines = sum(
            1 for p in self.registered_pipelines.values() if p["enabled"]
        )
        running_executions = sum(
            1 for e in self.active_executions.values() if e.status == "running"
        )

        return {
            "orchestrator_status": self.status.value,
            "registered_pipelines": len(self.registered_pipelines),
            "active_pipelines": active_pipelines,
            "running_executions": running_executions,
            "registered_tasks": len(self.task_registry),
            "platform_health": (
                self.core_platform.get_platform_status()
                if self.core_platform
                else "unknown"
            ),
            "timestamp": datetime.now().isoformat(),
        }


# Integrações específicas para cada componente
class PrefectIntegration:
    """Integração com Prefect"""

    async def get_flow_runs(self) -> List[Dict[str, Any]]:
        """Obtém execuções de flows do Prefect"""
        # Implementação real conectaria com a API do Prefect
        return []

    async def trigger_flow(
        self, flow_name: str, parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Dispara um flow no Prefect"""
        # Implementação real usaria a API do Prefect
        return f"flow_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


class SparkIntegration:
    """Integração com Spark"""

    async def sync_data_layers(self) -> Dict[str, Any]:
        """Sincroniza dados entre camadas do Data Lake"""
        # Implementação real usaria PySpark
        return {
            "layers_synced": 3,
            "records_processed": 125000,
            "duration_seconds": 45.2,
        }

    async def get_cluster_status(self) -> Dict[str, Any]:
        """Obtém status do cluster Spark"""
        return {
            "master_status": "alive",
            "workers": 2,
            "running_applications": 1,
            "available_cores": 8,
            "available_memory": "16GB",
        }


class MLflowIntegration:
    """Integração com MLflow"""

    async def get_latest_models(self) -> List[Dict[str, Any]]:
        """Obtém modelos mais recentes"""
        return []

    async def deploy_model(self, model_name: str, version: str) -> Dict[str, Any]:
        """Faz deploy de um modelo"""
        return {
            "deployment_id": f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "model_name": model_name,
            "version": version,
            "status": "deployed",
        }


class KafkaIntegration:
    """Integração com Kafka"""

    async def publish_event(self, topic: str, event: Dict[str, Any]):
        """Publica evento no Kafka"""
        # Implementação real usaria kafka-python
        pass

    async def get_topic_metrics(self) -> Dict[str, Any]:
        """Obtém métricas dos tópicos"""
        return {"total_topics": 4, "total_messages": 15670, "message_rate": 125.5}


class MonitoringIntegration:
    """Integração com sistema de monitoramento"""

    async def collect_metrics(self) -> Dict[str, Any]:
        """Coleta métricas da plataforma"""
        return {
            "cpu_usage": 65.4,
            "memory_usage": 78.2,
            "disk_usage": 45.1,
            "network_io": 1250.5,
        }

    async def send_alert(self, alert: Dict[str, Any]):
        """Envia alerta"""
        # Implementação real enviaria via email/slack/etc
        pass


# Instância global do orquestrador
unified_orchestrator = UnifiedOrchestrator()

# Registrar pipelines padrão
unified_orchestrator.register_pipeline(
    name="platform_health_check",
    tasks=["health_check"],
    schedule="*/5 * * * *",  # A cada 5 minutos
    enabled=True,
)

unified_orchestrator.register_pipeline(
    name="data_pipeline_full",
    tasks=["health_check", "data_sync", "data_quality"],
    schedule="0 6 * * *",  # Diário às 06:00
    enabled=True,
)

unified_orchestrator.register_pipeline(
    name="maintenance_pipeline",
    tasks=["backup", "health_check"],
    schedule="0 3 * * 6",  # Sábados às 03:00
    enabled=True,
)


# Função utilitária para acesso fácil
async def execute_unified_pipeline(
    pipeline_name: str, parameters: Optional[Dict[str, Any]] = None
) -> PipelineExecution:
    """Executa um pipeline unificado"""
    return await unified_orchestrator.execute_pipeline(pipeline_name, parameters)


def get_unified_metrics() -> Dict[str, Any]:
    """Obtém métricas unificadas da plataforma"""
    return unified_orchestrator.get_platform_metrics()


if __name__ == "__main__":
    # Exemplo de uso
    async def main():
        print("🚀 Inicializando Orquestrador Unificado...")

        # Obter métricas da plataforma
        metrics = get_unified_metrics()
        print(f"📊 Pipelines registrados: {metrics['registered_pipelines']}")
        print(f"📊 Tasks registradas: {metrics['registered_tasks']}")

        # Executar pipeline de health check
        execution = await execute_unified_pipeline("platform_health_check")
        print(f"✅ Execução {execution.id}: {execution.status}")

        # Mostrar status de todos os pipelines
        for pipeline_name in unified_orchestrator.registered_pipelines:
            status = unified_orchestrator.get_pipeline_status(pipeline_name)
            print(
                f"🔄 {pipeline_name}: {status['success_count']} sucessos, {status['failure_count']} falhas"
            )

    asyncio.run(main())
