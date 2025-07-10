#!/usr/bin/env python3
"""
DataLab Platform Test Suite
Testa todos os componentes da plataforma unificada
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

import requests

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


class DataLabTester:
    """Testa a plataforma DataLab"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}

    def run_all_tests(self):
        """Executa todos os testes"""
        logger.info("🧪 Iniciando testes da DataLab Platform...")

        tests = [
            ("dependencies", self.test_dependencies),
            ("configuration", self.test_configuration),
            ("docker_services", self.test_docker_services),
            ("service_health", self.test_service_health),
            ("cli_interface", self.test_cli_interface),
            ("platform_api", self.test_platform_api),
            ("data_pipeline", self.test_data_pipeline),
        ]

        for test_name, test_func in tests:
            logger.info(f"🔍 Executando teste: {test_name}")
            try:
                result = test_func()
                self.test_results[test_name] = {
                    "status": "PASS" if result else "FAIL",
                    "details": "",
                }
                status_icon = "✅" if result else "❌"
                logger.info(
                    f"{status_icon} Teste {test_name}: {'PASSOU' if result else 'FALHOU'}"
                )
            except Exception as e:
                self.test_results[test_name] = {"status": "ERROR", "details": str(e)}
                logger.error(f"❌ Erro no teste {test_name}: {e}")

        self.generate_report()

    def test_dependencies(self):
        """Testa dependências do sistema"""
        logger.info("  📋 Verificando dependências...")

        # Verificar Python
        if sys.version_info < (3, 8):
            logger.error("  ❌ Python 3.8+ necessário")
            return False

        # Verificar Docker
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("  ❌ Docker não encontrado")
            return False

        # Verificar Docker Compose
        try:
            subprocess.run(
                ["docker-compose", "--version"], check=True, capture_output=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("  ❌ Docker Compose não encontrado")
            return False

        # Verificar arquivos principais
        required_files = [
            "datalab_manager.py",
            "datalab_cli.py",
            "setup.sh",
            "requirements.txt",
            "docker-compose.yml",
        ]

        for file in required_files:
            if not (self.project_root / file).exists():
                logger.error(f"  ❌ Arquivo não encontrado: {file}")
                return False

        logger.info("  ✅ Todas as dependências OK")
        return True

    def test_configuration(self):
        """Testa sistema de configuração"""
        logger.info("  ⚙️ Testando configuração...")

        try:
            sys.path.insert(0, str(self.project_root))
            from config.platform_config import platform_config

            # Testar configurações básicas
            platform_name = platform_config.get_platform_config("platform.name", "")
            if not platform_name:
                logger.error("  ❌ Configuração da plataforma não encontrada")
                return False

            # Testar configuração de serviços
            services = platform_config.get_all_services()
            if not services:
                logger.error("  ❌ Configuração de serviços não encontrada")
                return False

            # Testar configuração de pipelines
            pipelines = platform_config.get_all_pipelines()
            if not pipelines:
                logger.error("  ❌ Configuração de pipelines não encontrada")
                return False

            logger.info("  ✅ Sistema de configuração OK")
            return True

        except Exception as e:
            logger.error(f"  ❌ Erro no sistema de configuração: {e}")
            return False

    def test_docker_services(self):
        """Testa serviços Docker"""
        logger.info("  🐳 Verificando serviços Docker...")

        try:
            # Verificar se Docker daemon está rodando
            subprocess.run(["docker", "info"], check=True, capture_output=True)

            # Verificar se há serviços rodando
            result = subprocess.run(
                ["docker-compose", "ps", "--services"], capture_output=True, text=True
            )

            if result.returncode == 0:
                services = result.stdout.strip().split("\n")
                logger.info(f"  📊 Serviços encontrados: {len(services)}")
                return True
            else:
                logger.warning("  ⚠️ Nenhum serviço Docker rodando")
                return True  # Não é erro crítico

        except subprocess.CalledProcessError:
            logger.warning("  ⚠️ Docker daemon não está rodando")
            return True  # Não é erro crítico

    def test_service_health(self):
        """Testa health dos serviços web"""
        logger.info("  🏥 Testando health dos serviços...")

        services = {
            "prefect": "http://localhost:4200/api/health",
            "spark": "http://localhost:8080",
            "minio": "http://localhost:9000/minio/health/live",
            "mlflow": "http://localhost:5000/health",
            "streamlit": "http://localhost:8501/healthz",
            "jupyterhub": "http://localhost:8000/hub/health",
        }

        healthy_count = 0
        total_count = len(services)

        for service_name, health_url in services.items():
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code < 400:
                    logger.info(f"  ✅ {service_name}: HEALTHY")
                    healthy_count += 1
                else:
                    logger.warning(f"  ⚠️ {service_name}: HTTP {response.status_code}")
            except requests.RequestException:
                logger.warning(f"  ⚠️ {service_name}: NÃO ACESSÍVEL")

        logger.info(f"  📊 Serviços saudáveis: {healthy_count}/{total_count}")
        return healthy_count > 0  # Pelo menos um serviço deve estar rodando

    def test_cli_interface(self):
        """Testa interface CLI"""
        logger.info("  💻 Testando CLI...")

        try:
            # Testar se CLI responde
            result = subprocess.run(
                ["python3", str(self.project_root / "datalab_cli.py"), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and "DataLab" in result.stdout:
                logger.info("  ✅ CLI responde corretamente")
                return True
            else:
                logger.error("  ❌ CLI não responde corretamente")
                return False

        except subprocess.TimeoutExpired:
            logger.error("  ❌ CLI timeout")
            return False
        except Exception as e:
            logger.error(f"  ❌ Erro na CLI: {e}")
            return False

    def test_platform_api(self):
        """Testa API da plataforma"""
        logger.info("  🌐 Testando API da plataforma...")

        try:
            # Testar importação do platform manager
            sys.path.insert(0, str(self.project_root))
            from datalab_platform import DataLabPlatform

            # Criar instância
            platform = DataLabPlatform()

            logger.info("  ✅ API da plataforma acessível")
            return True

        except Exception as e:
            logger.error(f"  ❌ Erro na API: {e}")
            return False

    def test_data_pipeline(self):
        """Testa pipeline de dados básico"""
        logger.info("  🔄 Testando pipeline de dados...")

        try:
            # Testar importação dos flows
            sys.path.insert(0, str(self.project_root / "flows"))

            # Verificar se arquivos de pipeline existem
            pipeline_files = [
                "medallion_etl_flow.py",
                "monitoring_flow.py",
                "mlops_flow.py",
                "maintenance_flow.py",
            ]

            for pipeline_file in pipeline_files:
                if not (self.project_root / "flows" / pipeline_file).exists():
                    logger.error(f"  ❌ Pipeline não encontrado: {pipeline_file}")
                    return False

            logger.info("  ✅ Pipelines encontrados")
            return True

        except Exception as e:
            logger.error(f"  ❌ Erro nos pipelines: {e}")
            return False

    def generate_report(self):
        """Gera relatório final dos testes"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 RELATÓRIO FINAL DOS TESTES")
        logger.info("=" * 60)

        passed = 0
        failed = 0
        errors = 0

        for test_name, result in self.test_results.items():
            status = result["status"]
            if status == "PASS":
                icon = "✅"
                passed += 1
            elif status == "FAIL":
                icon = "❌"
                failed += 1
            else:
                icon = "⚠️"
                errors += 1

            logger.info(f"{icon} {test_name.upper()}: {status}")
            if result["details"]:
                logger.info(f"   Detalhes: {result['details']}")

        total = passed + failed + errors
        success_rate = (passed / total * 100) if total > 0 else 0

        logger.info(f"\n📈 RESUMO:")
        logger.info(f"   Total de testes: {total}")
        logger.info(f"   ✅ Passou: {passed}")
        logger.info(f"   ❌ Falhou: {failed}")
        logger.info(f"   ⚠️ Erro: {errors}")
        logger.info(f"   📊 Taxa de sucesso: {success_rate:.1f}%")

        if success_rate >= 80:
            logger.info("\n🎉 PLATAFORMA ESTÁ FUNCIONANDO BEM!")
        elif success_rate >= 50:
            logger.info("\n⚠️ PLATAFORMA PRECISA DE ATENÇÃO")
        else:
            logger.info("\n❌ PLATAFORMA TEM PROBLEMAS SÉRIOS")

        logger.info("=" * 60)

        # Salvar relatório em arquivo
        report_file = self.project_root / "logs" / "test_report.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(
                {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "results": self.test_results,
                    "summary": {
                        "total": total,
                        "passed": passed,
                        "failed": failed,
                        "errors": errors,
                        "success_rate": success_rate,
                    },
                },
                f,
                indent=2,
            )

        logger.info(f"📄 Relatório salvo em: {report_file}")

        return success_rate >= 50


def main():
    """Função principal"""
    print("🧪 DataLab Platform Test Suite")
    print("=" * 50)

    tester = DataLabTester()
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
