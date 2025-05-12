"""
NiFi Integration Example with DataLab Medallion Architecture

Este módulo demonstra como integrar o Apache NiFi com a arquitetura
Medallion (Bronze, Silver, Gold) já implementada no DataLab.
"""

import json
import os
import time
from datetime import datetime

import boto3
import requests
from botocore.client import Config

# Configurações do MinIO (S3 compatible)
S3_ENDPOINT = os.environ.get("S3_ENDPOINT", "http://minio:9000")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin")

# Configurações do NiFi
NIFI_API_URL = "https://localhost:8443/nifi-api"
NIFI_USERNAME = os.environ.get("NIFI_USERNAME", "admin")
NIFI_PASSWORD = os.environ.get("NIFI_PASSWORD", "admin123")


def get_s3_client():
    """
    Cria um cliente S3 para interagir com o MinIO

    Returns:
        boto3.client: Cliente S3 configurado para MinIO
    """
    s3_client = boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
    )
    return s3_client


def monitor_bronze_layer(bucket_name="bronze", prefix="raw_data_source1/"):
    """
    Monitora a camada Bronze do Data Lake (MinIO)

    Args:
        bucket_name (str): Nome do bucket para monitorar
        prefix (str): Prefixo/pasta para monitorar

    Returns:
        list: Lista de objetos encontrados
    """
    s3_client = get_s3_client()
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if "Contents" in response:
            return response["Contents"]
        return []
    except Exception as e:
        print(f"Erro ao monitorar camada bronze: {e}")
        return []


def create_nifi_connection(headers):
    """
    Exemplo de como criar uma conexão no NiFi via API

    Args:
        headers (dict): Cabeçalhos de autenticação

    Returns:
        dict: Resposta da API do NiFi
    """
    # Este é apenas um exemplo conceitual e precisaria ser adaptado ao NiFi real
    # A API do NiFi é extensa e requer conhecimento detalhado do modelo de dados
    process_group_url = f"{NIFI_API_URL}/process-groups/root"

    # Em uma implementação real, você obteria o ID do grupo de processos primeiro
    # e depois criaria processadores e conexões

    return {"message": "Este é um exemplo conceitual da API do NiFi"}


def trigger_medallion_process(source_path, target_layer):
    """
    Aciona um processamento na arquitetura Medallion via NiFi

    Args:
        source_path (str): Caminho do arquivo fonte
        target_layer (str): Camada alvo ('silver' ou 'gold')

    Returns:
        bool: Sucesso ou falha da operação
    """
    print(f"Processando {source_path} para a camada {target_layer}")
    # Em uma implementação real, isso acionaria um fluxo específico no NiFi
    # ou enviaria uma mensagem para um ponto de entrada do NiFi

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    print(f"Job iniciado em {timestamp}")

    # Simula um processamento bem-sucedido
    time.sleep(2)
    return True


def main():
    """Função principal de demonstração"""
    print("Iniciando integração NiFi com arquitetura Medallion")

    # 1. Monitorar a camada Bronze
    bronze_files = monitor_bronze_layer()
    print(f"Encontrados {len(bronze_files)} arquivos na camada Bronze")

    # 2. Para cada arquivo na camada Bronze, acionar processamento para Silver
    for file in bronze_files[:3]:  # Limitar aos primeiros 3 por demonstração
        file_key = file.get("Key")
        if file_key:
            success = trigger_medallion_process(file_key, "silver")
            if success:
                print(f"Arquivo {file_key} processado com sucesso para Silver")

    print("Integração NiFi com arquitetura Medallion concluída")


if __name__ == "__main__":
    main()
