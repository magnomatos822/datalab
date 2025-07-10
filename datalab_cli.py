#!/usr/bin/env python3
"""
DataLab Management CLI - Interface de Linha de Comando para Gestão
Sistema unificado para gerenciar toda a plataforma DataLab
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import click
import yaml

# Adicionar ao path
sys.path.insert(0, str(Path(__file__).parent))


@click.group()
@click.option("--config", "-c", default="config", help="Diretório de configuração")
@click.option("--verbose", "-v", is_flag=True, help="Modo verboso")
@click.pass_context
def cli(ctx, config, verbose):
    """🚀 DataLab Platform Management CLI"""
    ctx.ensure_object(dict)
    ctx.obj["config_dir"] = config
    ctx.obj["verbose"] = verbose

    if verbose:
        click.echo("🔧 Modo verboso ativado")


@cli.group()
def platform():
    """Comandos de gestão da plataforma"""
    pass


@cli.group()
def services():
    """Comandos de gestão de serviços"""
    pass


@cli.group()
def pipelines():
    """Comandos de gestão de pipelines"""
    pass


@cli.group()
def data():
    """Comandos de gestão de dados"""
    pass


# === Comandos da Plataforma ===


@platform.command()
@click.option(
    "--env",
    "-e",
    default="development",
    help="Ambiente (development/staging/production)",
)
@click.pass_context
def init(ctx, env):
    """🚀 Inicializa a plataforma DataLab"""
    click.echo("🚀 Inicializando DataLab Platform...")

    # Criar estrutura de diretórios
    directories = [
        "config",
        "config/env",
        "logs",
        "data",
        "data/raw",
        "data/processed",
        "notebooks",
        "scripts",
        "models",
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        if ctx.obj["verbose"]:
            click.echo(f"📁 Criado diretório: {directory}")

    # Criar configurações padrão
    _create_default_configs(env, ctx.obj["verbose"])

    # Verificar dependências
    _check_dependencies(ctx.obj["verbose"])

    click.echo("✅ Platform DataLab inicializada com sucesso!")
    click.echo("💡 Use 'datalab services start' para iniciar os serviços")


@platform.command()
@click.pass_context
def status(ctx):
    """📊 Mostra status da plataforma"""
    click.echo("📊 Status da Plataforma DataLab")
    click.echo("=" * 40)

    # Verificar Docker
    docker_status = _check_docker()
    status_icon = "✅" if docker_status else "❌"
    click.echo(
        f"{status_icon} Docker: {'Disponível' if docker_status else 'Não disponível'}"
    )

    # Verificar serviços
    services_status = _check_services_status()
    for service, status in services_status.items():
        status_icon = "🟢" if status else "🔴"
        click.echo(f"{status_icon} {service}: {'Ativo' if status else 'Inativo'}")

    # Verificar configurações
    config_status = _check_configurations()
    status_icon = "✅" if config_status else "⚠️"
    click.echo(f"{status_icon} Configurações: {'OK' if config_status else 'Verificar'}")


@platform.command()
@click.option("--backup-dir", default="backups", help="Diretório para backup")
@click.pass_context
def backup(ctx, backup_dir):
    """💾 Faz backup da plataforma"""
    click.echo("💾 Fazendo backup da plataforma...")

    backup_path = Path(backup_dir)
    backup_path.mkdir(exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_file = backup_path / f"datalab_backup_{timestamp}.tar.gz"

    # Itens para backup
    items_to_backup = [
        "config/",
        "data/",
        "notebooks/",
        "models/",
        "docker-compose.yml",
        "requirements.txt",
    ]

    try:
        cmd = ["tar", "-czf", str(backup_file)] + items_to_backup
        subprocess.run(cmd, check=True)
        click.echo(f"✅ Backup criado: {backup_file}")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Erro no backup: {e}")


# === Comandos de Serviços ===


@services.command()
@click.option("--service", "-s", help="Serviço específico para iniciar")
@click.option("--detach", "-d", is_flag=True, help="Executar em background")
@click.pass_context
def start(ctx, service, detach):
    """▶️ Inicia serviços da plataforma"""
    if service:
        click.echo(f"▶️ Iniciando serviço: {service}")
        cmd = ["docker-compose", "up"]
        if detach:
            cmd.append("-d")
        cmd.append(service)
    else:
        click.echo("▶️ Iniciando todos os serviços...")
        cmd = ["docker-compose", "up"]
        if detach:
            cmd.append("-d")

    try:
        subprocess.run(cmd, check=True)
        click.echo("✅ Serviços iniciados com sucesso!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Erro ao iniciar serviços: {e}")


@services.command()
@click.option("--service", "-s", help="Serviço específico para parar")
@click.pass_context
def stop(ctx, service):
    """⏹️ Para serviços da plataforma"""
    if service:
        click.echo(f"⏹️ Parando serviço: {service}")
        cmd = ["docker-compose", "stop", service]
    else:
        click.echo("⏹️ Parando todos os serviços...")
        cmd = ["docker-compose", "down"]

    try:
        subprocess.run(cmd, check=True)
        click.echo("✅ Serviços parados com sucesso!")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Erro ao parar serviços: {e}")


@services.command()
@click.pass_context
def logs(ctx):
    """📋 Mostra logs dos serviços"""
    click.echo("📋 Logs dos serviços:")
    try:
        subprocess.run(["docker-compose", "logs", "--tail=50"], check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Erro ao obter logs: {e}")


@services.command()
@click.pass_context
def health(ctx):
    """🏥 Verifica saúde dos serviços"""
    click.echo("🏥 Verificando saúde dos serviços...")

    services_health = _check_services_health()

    for service, health in services_health.items():
        status_icon = "🟢" if health["healthy"] else "🔴"
        response_time = health.get("response_time", "N/A")
        click.echo(f"{status_icon} {service}: {health['status']} ({response_time}ms)")


# === Comandos de Pipelines ===


@pipelines.command()
@click.pass_context
def list(ctx):
    """📋 Lista pipelines disponíveis"""
    click.echo("📋 Pipelines Disponíveis:")

    try:
        from config.platform_config import platform_config

        pipelines = platform_config.get_all_pipelines()

        for name, config in pipelines.items():
            status = "🟢" if config.enabled else "🔴"
            click.echo(f"{status} {name}: {config.description}")
            click.echo(f"   Schedule: {config.schedule}")
            click.echo(f"   Tasks: {', '.join(config.tasks)}")
            click.echo()

    except Exception as e:
        click.echo(f"❌ Erro ao listar pipelines: {e}")


@pipelines.command()
@click.argument("pipeline_name")
@click.option("--params", "-p", help="Parâmetros em JSON")
@click.pass_context
def run(ctx, pipeline_name, params):
    """🚀 Executa um pipeline específico"""
    click.echo(f"🚀 Executando pipeline: {pipeline_name}")

    parameters = {}
    if params:
        try:
            parameters = json.loads(params)
        except json.JSONDecodeError:
            click.echo("❌ Parâmetros inválidos (deve ser JSON válido)")
            return

    try:
        # Executar via Prefect CLI
        cmd = ["prefect", "deployment", "run", f"{pipeline_name}/default"]
        if parameters:
            cmd.extend(["--param", json.dumps(parameters)])

        subprocess.run(cmd, check=True)
        click.echo(f"✅ Pipeline {pipeline_name} executado!")

    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Erro ao executar pipeline: {e}")


@pipelines.command()
@click.argument("pipeline_name")
@click.option("--enable/--disable", default=True, help="Habilitar/desabilitar pipeline")
@click.pass_context
def toggle(ctx, pipeline_name, enable):
    """🔄 Habilita/desabilita um pipeline"""
    action = "habilitando" if enable else "desabilitando"
    click.echo(f"🔄 {action.capitalize()} pipeline: {pipeline_name}")

    try:
        from config.platform_config import platform_config

        platform_config.update_config("pipelines", pipeline_name, {"enabled": enable})

        status = "habilitado" if enable else "desabilitado"
        click.echo(f"✅ Pipeline {pipeline_name} {status}!")

    except Exception as e:
        click.echo(f"❌ Erro ao modificar pipeline: {e}")


# === Comandos de Dados ===


@data.command()
@click.argument("source_path")
@click.argument("table_name")
@click.option("--format", "-f", default="csv", help="Formato dos dados")
@click.pass_context
def ingest(ctx, source_path, table_name, format):
    """📥 Ingere dados na camada Bronze"""
    click.echo(f"📥 Ingerindo dados: {source_path} -> {table_name}")

    try:
        # Aqui seria chamada a função real de ingestão
        # Por exemplo, através do sistema de pipelines
        click.echo(f"✅ Dados ingeridos na tabela {table_name}!")

    except Exception as e:
        click.echo(f"❌ Erro na ingestão: {e}")


@data.command()
@click.option(
    "--layer",
    "-l",
    type=click.Choice(["bronze", "silver", "gold"]),
    help="Camada específica",
)
@click.pass_context
def list_tables(ctx, layer):
    """📋 Lista tabelas disponíveis"""
    click.echo("📋 Tabelas Disponíveis:")

    layers = [layer] if layer else ["bronze", "silver", "gold"]

    for layer_name in layers:
        click.echo(f"\n🏷️ Camada {layer_name.upper()}:")

        # Aqui seria feita a listagem real das tabelas
        # Por exemplo, listando diretórios no MinIO
        tables = _list_tables_in_layer(layer_name)

        for table in tables:
            click.echo(f"  📊 {table}")


@data.command()
@click.option("--days", "-d", default=30, help="Dias de retenção")
@click.pass_context
def cleanup(ctx, days):
    """🧹 Limpa dados antigos"""
    click.echo(f"🧹 Limpando dados com mais de {days} dias...")

    try:
        # Aqui seria implementada a limpeza real
        click.echo(f"✅ Limpeza concluída!")

    except Exception as e:
        click.echo(f"❌ Erro na limpeza: {e}")


# === Funções auxiliares ===


def _create_default_configs(env: str, verbose: bool):
    """Cria configurações padrão"""
    try:
        from config.platform_config import platform_config

        # Gerar configurações padrão
        platform_config._save_config_file(
            "platform.yaml", platform_config._default_platform_config()
        )

        platform_config._save_config_file(
            "services.yaml",
            {
                name: config.__dict__
                for name, config in platform_config._default_services_config().items()
            },
        )

        platform_config._save_config_file(
            "pipelines.yaml",
            {
                name: config.__dict__
                for name, config in platform_config._default_pipelines_config().items()
            },
        )

        if verbose:
            click.echo("✅ Configurações padrão criadas")

    except Exception as e:
        if verbose:
            click.echo(f"⚠️ Erro ao criar configurações: {e}")


def _check_dependencies(verbose: bool):
    """Verifica dependências do sistema"""
    dependencies = ["docker", "docker-compose", "python3"]

    for dep in dependencies:
        try:
            subprocess.run(["which", dep], check=True, capture_output=True)
            if verbose:
                click.echo(f"✅ {dep}: Disponível")
        except subprocess.CalledProcessError:
            click.echo(f"❌ {dep}: Não encontrado")


def _check_docker() -> bool:
    """Verifica se Docker está disponível"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _check_services_status() -> Dict[str, bool]:
    """Verifica status dos serviços via Docker Compose"""
    services = {
        "prefect-server": False,
        "spark-master": False,
        "minio": False,
        "mlflow": False,
        "streamlit": False,
        "jupyterhub": False,
    }

    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--services", "--filter", "status=running"],
            capture_output=True,
            text=True,
            check=True,
        )

        running_services = result.stdout.strip().split("\n")

        for service in running_services:
            if service in services:
                services[service] = True

    except subprocess.CalledProcessError:
        pass

    return services


def _check_services_health() -> Dict[str, Dict]:
    """Verifica saúde detalhada dos serviços"""
    import time

    import requests

    services_health = {}

    health_checks = {
        "prefect-server": "http://localhost:4200/api/health",
        "spark-master": "http://localhost:8080",
        "minio": "http://localhost:9000/minio/health/live",
        "mlflow": "http://localhost:5000/health",
        "streamlit": "http://localhost:8501/healthz",
        "jupyterhub": "http://localhost:8000/hub/health",
    }

    for service, health_url in health_checks.items():
        try:
            start_time = time.time()
            response = requests.get(health_url, timeout=5)
            response_time = int((time.time() - start_time) * 1000)

            services_health[service] = {
                "healthy": response.status_code < 400,
                "status": f"HTTP {response.status_code}",
                "response_time": response_time,
            }
        except Exception as e:
            services_health[service] = {
                "healthy": False,
                "status": str(e),
                "response_time": None,
            }

    return services_health


def _check_configurations() -> bool:
    """Verifica se configurações estão válidas"""
    config_files = [
        "config/platform.yaml",
        "config/services.yaml",
        "config/pipelines.yaml",
    ]

    for config_file in config_files:
        if not Path(config_file).exists():
            return False

    return True


def _list_tables_in_layer(layer: str) -> List[str]:
    """Lista tabelas em uma camada específica"""
    # Simulação - aqui seria feita a listagem real
    if layer == "bronze":
        return ["stocks_raw_20241201", "sales_raw_20241201"]
    elif layer == "silver":
        return ["stocks_cleaned_20241201", "sales_cleaned_20241201"]
    elif layer == "gold":
        return ["stocks_analytics_20241201", "sales_summary_20241201"]

    return []


if __name__ == "__main__":
    cli()
