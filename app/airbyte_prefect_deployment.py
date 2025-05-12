"""
Integração do Airbyte com fluxos Prefect
"""

import json
import os
import time
from datetime import datetime

import requests
from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner


@task(name="Login no Airbyte")
def login_to_airbyte(
    host="http://airbyte-server:8000/api/v1", username="airbyte", password="password"
):
    """
    Autentica com o servidor Airbyte

    Args:
        host: URL base para a API do Airbyte
        username: Nome de usuário para autenticação
        password: Senha para autenticação

    Returns:
        token: Token de autenticação
    """
    login_url = f"{host}/login"
    response = requests.post(
        login_url, json={"username": username, "password": password}
    )

    if response.status_code != 200:
        raise Exception(f"Falha ao autenticar no Airbyte: {response.text}")

    token = response.json().get("token")
    print("Autenticação com Airbyte bem-sucedida")
    return token, host


@task(name="Criar Fonte")
def create_source(token_host, name, source_type, configuration):
    """
    Cria uma nova fonte no Airbyte

    Args:
        token_host: Tupla (token, host_url)
        name: Nome da fonte
        source_type: Tipo da fonte (postgres, mysql, etc)
        configuration: Configuração específica para a fonte
    """
    token, host = token_host
    url = f"{host}/sources/create"
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "name": name,
        "sourceDefinitionId": source_type,
        "connectionConfiguration": configuration,
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"Falha ao criar fonte: {response.text}")

    print(f"Fonte '{name}' criada com sucesso!")
    return response.json()


@task(name="Criar Destino")
def create_destination(token_host, name, destination_type, configuration):
    """
    Cria um novo destino no Airbyte

    Args:
        token_host: Tupla (token, host_url)
        name: Nome do destino
        destination_type: Tipo do destino (ex: id do MinIO)
        configuration: Configuração específica para o destino
    """
    token, host = token_host
    url = f"{host}/destinations/create"
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "name": name,
        "destinationDefinitionId": destination_type,
        "connectionConfiguration": configuration,
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"Falha ao criar destino: {response.text}")

    print(f"Destino '{name}' criado com sucesso!")
    return response.json()


@task(name="Criar Conexão")
def create_connection(
    token_host, name, source_id, destination_id, streams, sync_mode="full_refresh"
):
    """
    Cria uma nova conexão entre fonte e destino

    Args:
        token_host: Tupla (token, host_url)
        name: Nome da conexão
        source_id: ID da fonte
        destination_id: ID do destino
        streams: Lista de streams para sincronizar
        sync_mode: Modo de sincronização (full_refresh ou incremental)
    """
    token, host = token_host
    url = f"{host}/connections/create"
    headers = {"Authorization": f"Bearer {token}"}

    sync_catalog = {"streams": streams}

    data = {
        "name": name,
        "sourceId": source_id,
        "destinationId": destination_id,
        "syncCatalog": sync_catalog,
        "status": "active",
        "schedule": {"units": 24, "timeUnit": "hours"},
        "namespaceFormat": "${SOURCE_NAMESPACE}",
        "prefix": "",
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"Falha ao criar conexão: {response.text}")

    print(f"Conexão '{name}' criada com sucesso!")
    return response.json()


@task(name="Disparar Sincronização")
def trigger_sync(token_host, connection_id):
    """
    Dispara uma sincronização manual

    Args:
        token_host: Tupla (token, host_url)
        connection_id: ID da conexão a ser sincronizada
    """
    token, host = token_host
    url = f"{host}/connections/sync"
    headers = {"Authorization": f"Bearer {token}"}

    data = {"connectionId": connection_id}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"Falha ao iniciar sincronização: {response.text}")

    print(f"Sincronização da conexão {connection_id} iniciada!")
    job_id = response.json().get("job", {}).get("id")
    return token_host, job_id


@task(name="Monitorar Sincronização", max_retries=5, retry_delay_seconds=30)
def monitor_sync(token_job, timeout=300):
    """
    Monitora o status de uma sincronização

    Args:
        token_job: Tupla ((token, host), job_id)
        timeout: Timeout em segundos
    """
    (token, host), job_id = token_job
    url = f"{host}/jobs/get"
    headers = {"Authorization": f"Bearer {token}"}

    start_time = time.time()

    while time.time() - start_time < timeout:
        data = {"id": job_id}

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            print(f"Falha ao verificar status do job: {response.text}")
            time.sleep(10)
            continue

        status = response.json().get("job", {}).get("status")
        print(f"Status da sincronização: {status}")

        if status == "succeeded":
            return True, job_id
        elif status in ["failed", "cancelled"]:
            return False, job_id

        time.sleep(10)

    print(f"Timeout após {timeout} segundos.")
    return False, job_id


@flow(
    name="Airbyte to MinIO Bronze",
    description="Fluxo para ingerir dados de uma fonte para o MinIO (camada Bronze) via Airbyte",
)
def airbyte_to_minio_flow(
    source_name, source_type, source_config, streams, prefix="raw_data"
):
    """
    Fluxo Prefect para configuração e execução de uma sincronização Airbyte

    Args:
        source_name: Nome da fonte
        source_type: Tipo da fonte (ID)
        source_config: Configuração da fonte
        streams: Lista de streams para sincronizar
        prefix: Prefixo para os dados no bucket
    """
    # Timestamp para nomes únicos
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Login no Airbyte
    token_host = login_to_airbyte()

    # Criar fonte
    source = create_source(
        token_host=token_host,
        name=f"{source_name}_{timestamp}",
        source_type=source_type,
        configuration=source_config,
    )

    # Criar destino (MinIO / camada Bronze)
    destination = create_destination(
        token_host=token_host,
        name=f"Bronze_{source_name}_{timestamp}",
        destination_type="4816b78f-1489-44c1-9060-4b19d5fa9362",  # S3
        configuration={
            "endpoint": "http://minio:9000",
            "access_key_id": "admin",
            "secret_access_key": "admin123",
            "bucket_name": "bronze",
            "path_prefix": f"{prefix}/{source_name}",
        },
    )

    # Criar conexão
    connection = create_connection(
        token_host=token_host,
        name=f"{source_name}_to_bronze_{timestamp}",
        source_id=source["sourceId"],
        destination_id=destination["destinationId"],
        streams=streams,
    )

    # Disparar sincronização
    sync_job = trigger_sync(
        token_host=token_host, connection_id=connection["connectionId"]
    )

    # Monitorar sincronização
    success, job_id = monitor_sync(token_job=sync_job)

    if success:
        print(f"Sincronização concluída com sucesso! Job ID: {job_id}")
    else:
        print(f"Falha na sincronização. Job ID: {job_id}")

    return {
        "success": success,
        "source_id": source["sourceId"],
        "destination_id": destination["destinationId"],
        "connection_id": connection["connectionId"],
        "job_id": job_id,
        "path": f"s3a://bronze/{prefix}/{source_name}",
    }


# Exemplo de uso
if __name__ == "__main__":
    # Exemplo: Configurar uma sincronização de PostgreSQL para MinIO Bronze
    result = airbyte_to_minio_flow(
        source_name="postgres_sample",
        source_type="decd338e-5647-4c0b-adf4-da0e75f5a750",  # PostgreSQL
        source_config={
            "host": "postgres",
            "port": 5432,
            "database": "sample_db",
            "username": "postgres",
            "password": "postgres",
            "schema": "public",
        },
        streams=[
            {
                "name": "users",
                "syncMode": "full_refresh",
                "destinationSyncMode": "overwrite",
            },
            {
                "name": "orders",
                "syncMode": "full_refresh",
                "destinationSyncMode": "overwrite",
            },
        ],
    )

    print(f"Resultado do fluxo: {result}")
