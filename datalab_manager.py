#!/usr/bin/env python3
"""
DataLab Unified Manager - Gestor Unificado da Plataforma
Sistema integrado para inicialização, monitoramento e gestão da plataforma completa
"""

import json
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/datalab_manager.log")],
)

logger = logging.getLogger(__name__)


class DataLabManager:
    """
    Gestor Unificado da Plataforma DataLab
    Responsável por inicializar, monitorar e gerenciar todos os componentes
    """

    def __init__(self):
        """Inicializa o gestor da plataforma"""
        self.project_root = Path(__file__).parent
        self.services = {}
        self.pipelines = {}
        self.monitoring_active = False
        self.shutdown_requested = False

        # Configurar handler para shutdown gracioso
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("🚀 DataLab Manager inicializado")

    def _signal_handler(self, signum, frame):
        """Handler para sinais de shutdown"""
        logger.info(f"📡 Sinal recebido: {signum}")
        self.shutdown_requested = True
        self.shutdown()

    def initialize_platform(self):
        """Inicializa completamente a plataforma"""
        logger.info("🚀 Inicializando DataLab Platform...")

        try:
            # 1. Verificar pré-requisitos
            self._check_prerequisites()

            # 2. Criar estrutura de diretórios
            self._create_directory_structure()

            # 3. Gerar configurações
            self._generate_configurations()

            # 4. Inicializar Docker Compose
            self._initialize_docker_services()

            # 5. Aguardar serviços ficarem prontos
            self._wait_for_services()

            # 6. Configurar Prefect
            self._configure_prefect()

            # 7. Registrar pipelines
            self._register_pipelines()

            # 8. Iniciar monitoramento
            self._start_monitoring()

            logger.info("✅ DataLab Platform inicializada com sucesso!")
            return True

        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            return False

    def _check_prerequisites(self):
        """Verifica pré-requisitos do sistema"""
        logger.info("🔍 Verificando pré-requisitos...")

        # Verificar Docker
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            logger.info("✅ Docker disponível")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("❌ Docker não encontrado")

        # Verificar Docker Compose
        try:
            subprocess.run(
                ["docker-compose", "--version"], check=True, capture_output=True
            )
            logger.info("✅ Docker Compose disponível")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("❌ Docker Compose não encontrado")

        # Verificar Python
        if sys.version_info < (3, 8):
            raise RuntimeError("❌ Python 3.8+ necessário")
        logger.info("✅ Python compatível")

    def _create_directory_structure(self):
        """Cria estrutura de diretórios necessária"""
        logger.info("📁 Criando estrutura de diretórios...")

        directories = [
            "logs",
            "data/bronze/raw_data_source1/table1",
            "data/bronze/raw_data_source2/table1",
            "data/bronze/logs",
            "data/silver/clean_data_domain1/table1",
            "data/silver/clean_data_domain2",
            "data/silver/metrics",
            "data/gold/analytics_domain1/dashboard1",
            "data/gold/analytics_domain2/view1",
            "data/gold/ml_features",
            "data/minio/mlflow/artifacts",
            "data/minio/mlflow/models",
            "config/env",
            "notebooks/shared",
            "models/staging",
            "models/production",
            "scripts/automation",
            "backups",
        ]

        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"📁 Criado: {directory}")

        logger.info("✅ Estrutura de diretórios criada")

    def _generate_configurations(self):
        """Gera configurações necessárias"""
        logger.info("⚙️ Gerando configurações...")

        # Configuração principal da plataforma
        platform_config = {
            "platform": {
                "name": "DataLab",
                "version": "2.0.0",
                "environment": os.getenv("DATALAB_ENV", "development"),
                "initialized_at": datetime.now().isoformat(),
                "components": {
                    "prefect": {"enabled": True, "version": "3.4.1"},
                    "spark": {"enabled": True, "version": "3.5"},
                    "minio": {"enabled": True, "version": "latest"},
                    "mlflow": {"enabled": True, "version": "2.22.0"},
                    "streamlit": {"enabled": True, "version": "1.45.0"},
                    "jupyterhub": {"enabled": True, "version": "5.3.0"},
                },
            },
            "storage": {
                "data_lake": {
                    "provider": "minio",
                    "endpoint": "http://localhost:9000",
                    "access_key": "minio",
                    "secret_key": "minio123",
                    "region": "us-east-1",
                }
            },
            "compute": {
                "spark": {
                    "master_url": "spark://localhost:7077",
                    "executor_memory": "2g",
                    "driver_memory": "1g",
                    "executor_cores": 2,
                }
            },
            "orchestration": {
                "prefect": {
                    "api_url": "http://localhost:4200/api",
                    "ui_url": "http://localhost:4200",
                }
            },
            "monitoring": {
                "health_check_interval": 30,
                "metrics_collection_interval": 60,
                "alert_thresholds": {
                    "cpu_usage": 80,
                    "memory_usage": 85,
                    "disk_usage": 90,
                },
            },
        }

        # Salvar configuração
        config_file = self.project_root / "config" / "platform.json"
        with open(config_file, "w") as f:
            json.dump(platform_config, f, indent=2)

        logger.info("✅ Configurações geradas")

    def _initialize_docker_services(self):
        """Inicializa serviços Docker"""
        logger.info("🐳 Inicializando serviços Docker...")

        try:
            # Build de imagens personalizadas se necessário
            subprocess.run(
                ["docker-compose", "build"], cwd=self.project_root, check=True
            )

            # Iniciar todos os serviços
            subprocess.run(
                ["docker-compose", "up", "-d"], cwd=self.project_root, check=True
            )

            logger.info("✅ Serviços Docker iniciados")

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao iniciar Docker: {e}")
            raise

    def _wait_for_services(self):
        """Aguarda todos os serviços ficarem prontos"""
        logger.info("⏳ Aguardando serviços ficarem prontos...")

        services_health = {
            "prefect-server": {
                "url": "http://localhost:4200/api/health",
                "timeout": 120,
            },
            "spark-master": {"url": "http://localhost:8080", "timeout": 60},
            "minio": {"url": "http://localhost:9000/minio/health/live", "timeout": 60},
            "mlflow": {"url": "http://localhost:5000/health", "timeout": 90},
            "streamlit": {"url": "http://localhost:8501/healthz", "timeout": 60},
            "jupyterhub": {"url": "http://localhost:8000/hub/health", "timeout": 90},
        }

        import requests

        for service_name, config in services_health.items():
            logger.info(f"⏳ Aguardando {service_name}...")

            timeout = config["timeout"]
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    response = requests.get(config["url"], timeout=5)
                    if response.status_code < 400:
                        logger.info(f"✅ {service_name} pronto")
                        self.services[service_name] = {
                            "status": "ready",
                            "url": config["url"],
                        }
                        break
                except requests.RequestException:
                    pass

                time.sleep(5)
            else:
                logger.warning(f"⚠️ {service_name} não respondeu em {timeout}s")
                self.services[service_name] = {
                    "status": "timeout",
                    "url": config["url"],
                }

        ready_services = len(
            [s for s in self.services.values() if s["status"] == "ready"]
        )
        total_services = len(services_health)

        logger.info(f"📊 Serviços prontos: {ready_services}/{total_services}")

    def _configure_prefect(self):
        """Configura Prefect"""
        logger.info("🔧 Configurando Prefect...")

        try:
            # Configurar API URL
            os.environ["PREFECT_API_URL"] = "http://localhost:4200/api"

            # Criar work pool se não existir
            try:
                subprocess.run(
                    [
                        "prefect",
                        "work-pool",
                        "create",
                        "default-agent-pool",
                        "--type",
                        "process",
                    ],
                    check=True,
                    capture_output=True,
                )
                logger.info("✅ Work pool criado")
            except subprocess.CalledProcessError:
                logger.info("ℹ️ Work pool já existe")

            logger.info("✅ Prefect configurado")

        except Exception as e:
            logger.warning(f"⚠️ Erro na configuração do Prefect: {e}")

    def _register_pipelines(self):
        """Registra pipelines no Prefect"""
        logger.info("📋 Registrando pipelines...")

        pipeline_files = [
            "flows/medallion_etl_flow.py",
            "flows/monitoring_flow.py",
            "flows/mlops_flow.py",
            "flows/maintenance_flow.py",
        ]

        for pipeline_file in pipeline_files:
            pipeline_path = self.project_root / pipeline_file

            if pipeline_path.exists():
                try:
                    # Executar script para registrar deployment
                    subprocess.run(
                        ["python", str(pipeline_path)],
                        cwd=self.project_root,
                        check=True,
                        capture_output=True,
                    )

                    pipeline_name = pipeline_path.stem
                    self.pipelines[pipeline_name] = {
                        "status": "registered",
                        "file": str(pipeline_path),
                    }

                    logger.info(f"✅ Pipeline registrado: {pipeline_name}")

                except subprocess.CalledProcessError as e:
                    logger.warning(f"⚠️ Erro ao registrar {pipeline_file}: {e}")
                    self.pipelines[pipeline_path.stem] = {
                        "status": "error",
                        "file": str(pipeline_path),
                    }
            else:
                logger.warning(f"⚠️ Pipeline não encontrado: {pipeline_file}")

        registered = len(
            [p for p in self.pipelines.values() if p["status"] == "registered"]
        )
        total = len(pipeline_files)

        logger.info(f"📊 Pipelines registrados: {registered}/{total}")

    def _start_monitoring(self):
        """Inicia monitoramento da plataforma"""
        logger.info("👁️ Iniciando monitoramento...")

        self.monitoring_active = True

        # Iniciar thread de monitoramento
        monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitoring_thread.start()

        logger.info("✅ Monitoramento ativo")

    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.monitoring_active and not self.shutdown_requested:
            try:
                # Verificar saúde dos serviços
                self._check_services_health()

                # Verificar uso de recursos
                self._check_system_resources()

                # Verificar logs de erro
                self._check_error_logs()

                # Aguardar próximo ciclo
                time.sleep(30)

            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                time.sleep(60)  # Aguardar mais tempo em caso de erro

    def _check_services_health(self):
        """Verifica saúde dos serviços"""
        import requests

        for service_name, config in self.services.items():
            if config["status"] == "ready":
                try:
                    response = requests.get(config["url"], timeout=5)
                    if response.status_code >= 400:
                        logger.warning(
                            f"⚠️ {service_name} não está saudável: HTTP {response.status_code}"
                        )
                        config["status"] = "unhealthy"
                    else:
                        config["status"] = "healthy"
                        config["last_check"] = datetime.now().isoformat()

                except requests.RequestException as e:
                    logger.warning(f"⚠️ {service_name} não acessível: {e}")
                    config["status"] = "unreachable"

    def _check_system_resources(self):
        """Verifica uso de recursos do sistema"""
        try:
            import psutil

            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                logger.warning(f"⚠️ Alto uso de CPU: {cpu_percent:.1f}%")

            # Memória
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                logger.warning(f"⚠️ Alto uso de memória: {memory.percent:.1f}%")

            # Disco
            disk = psutil.disk_usage("/")
            if disk.percent > 90:
                logger.warning(f"⚠️ Alto uso de disco: {disk.percent:.1f}%")

        except ImportError:
            pass  # psutil não disponível
        except Exception as e:
            logger.debug(f"Erro ao verificar recursos: {e}")

    def _check_error_logs(self):
        """Verifica logs em busca de erros"""
        log_file = self.project_root / "logs" / "datalab_manager.log"

        if log_file.exists():
            try:
                # Ler últimas 50 linhas em busca de erros
                with open(log_file, "r") as f:
                    lines = f.readlines()
                    recent_lines = lines[-50:]

                    error_count = sum(1 for line in recent_lines if "ERROR" in line)
                    if error_count > 5:
                        logger.warning(
                            f"⚠️ Muitos erros recentes detectados: {error_count}"
                        )

            except Exception as e:
                logger.debug(f"Erro ao verificar logs: {e}")

    def get_platform_status(self) -> Dict[str, Any]:
        """Retorna status completo da plataforma"""
        return {
            "platform": {
                "status": "running" if not self.shutdown_requested else "shutting_down",
                "uptime": time.time(),
                "monitoring_active": self.monitoring_active,
            },
            "services": self.services,
            "pipelines": self.pipelines,
            "timestamp": datetime.now().isoformat(),
        }

    def execute_pipeline(self, pipeline_name: str, parameters: Optional[Dict] = None):
        """Executa um pipeline específico"""
        logger.info(f"🚀 Executando pipeline: {pipeline_name}")

        try:
            cmd = ["prefect", "deployment", "run", f"{pipeline_name}/default"]

            if parameters:
                cmd.extend(["--params", json.dumps(parameters)])

            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True, check=True
            )

            logger.info(f"✅ Pipeline {pipeline_name} executado")
            return {"status": "success", "output": result.stdout}

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao executar pipeline {pipeline_name}: {e}")
            return {"status": "error", "error": str(e)}

    def shutdown(self):
        """Desliga a plataforma graciosamente"""
        logger.info("🛑 Iniciando shutdown da plataforma...")

        self.shutdown_requested = True
        self.monitoring_active = False

        try:
            # Parar serviços Docker
            subprocess.run(
                ["docker-compose", "down"], cwd=self.project_root, check=True
            )

            logger.info("✅ Serviços Docker parados")

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao parar serviços: {e}")

        logger.info("✅ DataLab Platform desligada")

    def run(self):
        """Executa a plataforma em modo interativo"""
        logger.info("🚀 Iniciando DataLab Platform...")

        if not self.initialize_platform():
            logger.error("❌ Falha na inicialização")
            return False

        logger.info("🎯 DataLab Platform está rodando!")
        logger.info("📊 Acesse o dashboard em: http://localhost:8501")
        logger.info("🔧 Acesse o Prefect UI em: http://localhost:4200")
        logger.info("📓 Acesse o JupyterHub em: http://localhost:8000")
        logger.info("🗂️ Acesse o MinIO Console em: http://localhost:9001")
        logger.info("🧪 Acesse o MLflow UI em: http://localhost:5000")

        try:
            # Manter plataforma rodando
            while not self.shutdown_requested:
                time.sleep(10)

        except KeyboardInterrupt:
            logger.info("🛑 Interrompido pelo usuário")

        finally:
            self.shutdown()

        return True


def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description="DataLab Platform Manager")
    parser.add_argument(
        "command",
        choices=["start", "stop", "status", "pipeline"],
        help="Comando a executar",
    )
    parser.add_argument("--pipeline-name", help="Nome do pipeline para executar")
    parser.add_argument("--params", help="Parâmetros do pipeline (JSON)")

    args = parser.parse_args()

    # Criar diretório de logs
    os.makedirs("logs", exist_ok=True)

    manager = DataLabManager()

    try:
        if args.command == "start":
            return manager.run()

        elif args.command == "stop":
            manager.shutdown()
            return True

        elif args.command == "status":
            status = manager.get_platform_status()
            print("📊 Status da DataLab Platform:")
            print(json.dumps(status, indent=2))
            return True

        elif args.command == "pipeline":
            if not args.pipeline_name:
                print("❌ Especifique --pipeline-name")
                return False

            params = None
            if args.params:
                params = json.loads(args.params)

            result = manager.execute_pipeline(args.pipeline_name, params)
            print(f"📊 Resultado: {json.dumps(result, indent=2)}")
            return result["status"] == "success"

    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
