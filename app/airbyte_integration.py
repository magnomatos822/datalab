"""
Módulo de integração com Airbyte
"""

import json
import os
import time
from datetime import datetime

import requests


class AirbyteClient:
    """Cliente para interagir com a API do Airbyte"""

    def __init__(
        self,
        host="http://airbyte-server:8000/api/v1",
        username="airbyte",
        password="password",
    ):
        """
        Inicializa o cliente Airbyte

        Args:
            host: URL base para a API do Airbyte
            username: Nome de usuário para autenticação
            password: Senha para autenticação
        """
        self.host = host
        self.username = username
        self.password = password
        self.token = None
        self.login()

    def login(self):
        """Autentica com o servidor Airbyte"""
        login_url = f"{self.host}/login"
        response = requests.post(
            login_url, json={"username": self.username, "password": self.password}
        )

        if response.status_code != 200:
            raise Exception(f"Falha ao autenticar no Airbyte: {response.text}")

        self.token = response.json().get("token")
        print("Autenticação com Airbyte bem-sucedida")

    def _make_request(self, method, endpoint, data=None):
        """
        Faz uma requisição para a API do Airbyte

        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Endpoint da API
            data: Dados para enviar (para POST, PUT, etc)
        """
        url = f"{self.host}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.token}"}

        if method.lower() == "get":
            response = requests.get(url, headers=headers)
        elif method.lower() == "post":
            response = requests.post(url, headers=headers, json=data)
        elif method.lower() == "put":
            response = requests.put(url, headers=headers, json=data)
        elif method.lower() == "delete":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Método desconhecido: {method}")

        return response

    def list_sources(self):
        """Lista todas as fontes configuradas"""
        response = self._make_request("GET", "sources/list")
        if response.status_code != 200:
            raise Exception(f"Falha ao listar fontes: {response.text}")
        return response.json().get("sources", [])

    def list_destinations(self):
        """Lista todos os destinos configurados"""
        response = self._make_request("GET", "destinations/list")
        if response.status_code != 200:
            raise Exception(f"Falha ao listar destinos: {response.text}")
        return response.json().get("destinations", [])

    def list_connections(self):
        """Lista todas as conexões configuradas"""
        response = self._make_request("GET", "connections/list")
        if response.status_code != 200:
            raise Exception(f"Falha ao listar conexões: {response.text}")
        return response.json().get("connections", [])

    def create_source(self, name, source_type, configuration):
        """
        Cria uma nova fonte no Airbyte

        Args:
            name: Nome da fonte
            source_type: Tipo da fonte (postgres, mysql, etc)
            configuration: Configuração específica para a fonte
        """
        data = {
            "name": name,
            "sourceDefinitionId": source_type,
            "connectionConfiguration": configuration,
        }

        response = self._make_request("POST", "sources/create", data)
        if response.status_code != 200:
            raise Exception(f"Falha ao criar fonte: {response.text}")
        return response.json()

    def create_destination(self, name, destination_type, configuration):
        """
        Cria um novo destino no Airbyte

        Args:
            name: Nome do destino
            destination_type: Tipo do destino (ex: id do MinIO)
            configuration: Configuração específica para o destino
        """
        data = {
            "name": name,
            "destinationDefinitionId": destination_type,
            "connectionConfiguration": configuration,
        }

        response = self._make_request("POST", "destinations/create", data)
        if response.status_code != 200:
            raise Exception(f"Falha ao criar destino: {response.text}")
        return response.json()

    def create_connection(
        self, name, source_id, destination_id, streams, sync_mode="full_refresh"
    ):
        """
        Cria uma nova conexão entre fonte e destino

        Args:
            name: Nome da conexão
            source_id: ID da fonte
            destination_id: ID do destino
            streams: Lista de streams para sincronizar
            sync_mode: Modo de sincronização (full_refresh ou incremental)
        """
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

        response = self._make_request("POST", "connections/create", data)
        if response.status_code != 200:
            raise Exception(f"Falha ao criar conexão: {response.text}")
        return response.json()

    def trigger_sync(self, connection_id):
        """
        Dispara uma sincronização manual

        Args:
            connection_id: ID da conexão a ser sincronizada
        """
        data = {"connectionId": connection_id}

        response = self._make_request("POST", "connections/sync", data)
        if response.status_code != 200:
            raise Exception(f"Falha ao iniciar sincronização: {response.text}")
        return response.json()

    def get_job_status(self, job_id):
        """
        Verifica o status de um job

        Args:
            job_id: ID do job a ser verificado
        """
        data = {"id": job_id}

        response = self._make_request("POST", "jobs/get", data)
        if response.status_code != 200:
            raise Exception(f"Falha ao verificar status do job: {response.text}")
        return response.json().get("job", {}).get("status")


# Exemplo de uso
def setup_minio_connection():
    """Configura uma conexão de exemplo do MinIO no Airbyte"""
    client = AirbyteClient()

    # Criar fonte PostgreSQL (exemplo)
    postgres_source = client.create_source(
        name="Demo Postgres",
        source_type="decd338e-5647-4c0b-adf4-da0e75f5a750",  # PostgreSQL
        configuration={
            "host": "postgres",
            "port": 5432,
            "database": "mydatabase",
            "username": "myuser",
            "password": "mypassword",
            "schema": "public",
        },
    )

    # Criar destino MinIO (S3)
    minio_destination = client.create_destination(
        name="Bronze Layer MinIO",
        destination_type="4816b78f-1489-44c1-9060-4b19d5fa9362",  # S3
        configuration={
            "endpoint": "http://minio:9000",
            "access_key_id": "admin",
            "secret_access_key": "admin123",
            "bucket_name": "bronze",
            "path_prefix": "raw_data",
        },
    )

    # Lista as tabelas disponíveis (normalmente viria da descoberta)
    streams = [
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
    ]

    # Cria uma conexão
    connection = client.create_connection(
        name="PostgreSQL to MinIO Bronze",
        source_id=postgres_source["sourceId"],
        destination_id=minio_destination["destinationId"],
        streams=streams,
    )

    # Inicia sincronização
    sync_job = client.trigger_sync(connection["connectionId"])

    job_id = sync_job["job"]["id"]
    status = "pending"

    # Monitora o status (com timeout)
    timeout = 300  # 5 minutos
    start_time = time.time()

    while status in ["pending", "running"]:
        if time.time() - start_time > timeout:
            print(f"Timeout após {timeout} segundos")
            break

        time.sleep(10)  # Verificar a cada 10 segundos
        status = client.get_job_status(job_id)
        print(f"Status da sincronização: {status}")

    print(f"Sincronização concluída com status: {status}")


if __name__ == "__main__":
    setup_minio_connection()
