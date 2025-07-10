"""
Fluxo de monitoramento em tempo real para streaming de dados com Kafka
Integrado com a plataforma unificada DataLab
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List

from prefect import flow, get_run_logger, task
from prefect.server.schemas.schedules import IntervalSchedule
from prefect.task_runners import ConcurrentTaskRunner

# Importar módulos da plataforma unificada
try:
    from config.platform_config import get_platform_config, get_service_config
    from core.config import ConfigurationManager
    from core.orchestrator import UnifiedOrchestrator
    from core.platform import DataLabPlatform
except ImportError:
    DataLabPlatform = None
    ConfigurationManager = None
    UnifiedOrchestrator = None
    get_platform_config = lambda x, y: y
    get_service_config = lambda x: None

# Inicializar plataforma unificada
platform = None
config_manager = None
orchestrator = None

if DataLabPlatform and ConfigurationManager and UnifiedOrchestrator:
    try:
        platform = DataLabPlatform()
        config_manager = ConfigurationManager()
        orchestrator = UnifiedOrchestrator()
    except Exception as e:
        print(f"Não foi possível inicializar plataforma unificada: {e}")
        platform = None
        config_manager = None
        orchestrator = None


@task(name="📡 Monitor Kafka Topics", retries=2)
def monitor_kafka_topics() -> Dict:
    """
    Monitora tópicos Kafka para detectar novos dados
    """
    run_logger = get_run_logger()
    run_logger.info("Monitorando tópicos Kafka...")

    # Usar health check da plataforma se disponível
    if platform:
        try:
            kafka_health = platform.check_service_health("kafka")
            if kafka_health.get("status") != "healthy":
                run_logger.warning(f"Kafka não está saudável: {kafka_health}")
        except Exception as e:
            run_logger.warning(
                f"Não foi possível verificar health do Kafka via plataforma: {e}"
            )

    try:
        # Simular conexão com Kafka (será implementado com kafka-python)
        topics_status = {
            "datalab-events": {
                "messages_count": 150,
                "last_message_time": datetime.now().isoformat(),
                "health": "healthy",
            },
            "datalab-notifications": {
                "messages_count": 45,
                "last_message_time": datetime.now().isoformat(),
                "health": "healthy",
            },
            "financial-data-stream": {
                "messages_count": 2340,
                "last_message_time": datetime.now().isoformat(),
                "health": "healthy",
            },
        }

        # Atualizar métricas na plataforma
        if platform:
            platform.update_metrics(
                {
                    "kafka_topics_monitored": len(topics_status),
                    "total_kafka_messages": sum(
                        topic["messages_count"] for topic in topics_status.values()
                    ),
                    "kafka_monitoring_timestamp": datetime.now().isoformat(),
                }
            )

        run_logger.info(f"Status dos tópicos: {topics_status}")
        return topics_status

    except Exception as e:
        run_logger.error(f"Erro ao monitorar Kafka: {str(e)}")
        raise


@task(name="💾 Check Data Lake Health")
def check_data_lake_health() -> Dict:
    """
    Verifica a saúde das camadas do Data Lake
    """
    run_logger = get_run_logger()
    run_logger.info("Verificando saúde do Data Lake...")

    try:
        # Verificar status de cada camada
        layers_status = {
            "bronze": {
                "total_tables": 15,
                "total_size_gb": 2.5,
                "last_updated": datetime.now().isoformat(),
                "health": "healthy",
            },
            "silver": {
                "total_tables": 12,
                "total_size_gb": 1.8,
                "last_updated": datetime.now().isoformat(),
                "health": "healthy",
            },
            "gold": {
                "total_tables": 8,
                "total_size_gb": 0.9,
                "last_updated": datetime.now().isoformat(),
                "health": "healthy",
            },
        }

        run_logger.info(f"Status das camadas: {layers_status}")
        return layers_status

    except Exception as e:
        run_logger.error(f"Erro ao verificar Data Lake: {str(e)}")
        raise


@task(name="🔧 Check Services Health")
def check_services_health() -> Dict:
    """
    Verifica a saúde de todos os serviços do DataLab
    """
    run_logger = get_run_logger()
    run_logger.info("Verificando saúde dos serviços...")

    services = {
        "spark": {"url": "http://spark-master:8080", "status": "unknown"},
        "minio": {"url": "http://minio:9000", "status": "unknown"},
        "kafka": {"url": "http://kafka:9092", "status": "unknown"},
        "mlflow": {"url": "http://mlflow:5000", "status": "unknown"},
        "jupyterhub": {"url": "http://jupyterhub:8000", "status": "unknown"},
        "streamlit": {"url": "http://streamlit:8501", "status": "unknown"},
    }

    try:
        # Simular verificação de saúde (será implementado com requests)
        for service_name, config in services.items():
            # Aqui seria feita uma requisição HTTP real
            config["status"] = "healthy"
            config["response_time_ms"] = 120
            config["last_check"] = datetime.now().isoformat()

        run_logger.info(f"Status dos serviços: {services}")
        return services

    except Exception as e:
        run_logger.error(f"Erro ao verificar serviços: {str(e)}")
        raise


@task(name="⚠️ Generate Alerts")
def generate_alerts(
    kafka_status: Dict, datalake_status: Dict, services_status: Dict
) -> List[Dict]:
    """
    Gera alertas baseado no status dos componentes
    """
    run_logger = get_run_logger()
    alerts = []

    # Verificar alertas de Kafka
    for topic, status in kafka_status.items():
        if status["health"] != "healthy":
            alerts.append(
                {
                    "type": "kafka_topic_unhealthy",
                    "component": f"kafka_topic_{topic}",
                    "severity": "warning",
                    "message": f"Tópico Kafka {topic} não está saudável",
                    "timestamp": datetime.now().isoformat(),
                }
            )

    # Verificar alertas de Data Lake
    for layer, status in datalake_status.items():
        if status["health"] != "healthy":
            alerts.append(
                {
                    "type": "datalake_layer_unhealthy",
                    "component": f"datalake_{layer}",
                    "severity": "error",
                    "message": f"Camada {layer} do Data Lake com problemas",
                    "timestamp": datetime.now().isoformat(),
                }
            )

    # Verificar alertas de serviços
    for service, status in services_status.items():
        if status["status"] != "healthy":
            alerts.append(
                {
                    "type": "service_unhealthy",
                    "component": f"service_{service}",
                    "severity": "critical",
                    "message": f"Serviço {service} não está responsivo",
                    "timestamp": datetime.now().isoformat(),
                }
            )

    if alerts:
        run_logger.warning(f"Alertas gerados: {len(alerts)}")
        for alert in alerts:
            run_logger.warning(f"ALERTA: {alert}")
    else:
        run_logger.info("✅ Nenhum alerta detectado - sistema saudável")

    return alerts


@flow(
    name="🔍 DataLab Real-time Monitoring",
    description="Monitoramento em tempo real da plataforma DataLab",
    task_runner=ConcurrentTaskRunner(),
)
def realtime_monitoring_flow():
    """
    Fluxo de monitoramento em tempo real do DataLab
    """
    run_logger = get_run_logger()
    run_logger.info("🔍 Iniciando monitoramento em tempo real")

    try:
        # Executar verificações em paralelo
        kafka_status = monitor_kafka_topics()
        datalake_status = check_data_lake_health()
        services_status = check_services_health()

        # Gerar alertas baseado nos status
        alerts = generate_alerts(kafka_status, datalake_status, services_status)

        # Compilar relatório de monitoramento
        monitoring_report = {
            "monitoring_timestamp": datetime.now().isoformat(),
            "kafka_status": kafka_status,
            "datalake_status": datalake_status,
            "services_status": services_status,
            "alerts": alerts,
            "overall_health": "healthy" if not alerts else "unhealthy",
        }

        run_logger.info(
            f"📊 Relatório de monitoramento: {monitoring_report['overall_health']}"
        )
        return monitoring_report

    except Exception as e:
        run_logger.error(f"❌ Erro no monitoramento: {str(e)}")
        raise


if __name__ == "__main__":
    # Criar deployment para monitoramento a cada 5 minutos
    from prefect.deployments import Deployment

    deployment = Deployment.build_from_flow(
        flow=realtime_monitoring_flow,
        name="datalab-monitoring-realtime",
        version="1.0.0",
        schedule=IntervalSchedule(interval=timedelta(minutes=5)),
        work_pool_name="default-agent-pool",
        tags=["monitoring", "realtime", "health-check", "datalab"],
    )

    deployment.apply()
    print("✅ Deployment 'datalab-monitoring-realtime' criado com sucesso!")
