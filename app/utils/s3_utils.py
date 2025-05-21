"""
Utilitários para trabalhar com MinIO/S3 de forma resiliente
"""

import io
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

import boto3
import pandas as pd
from botocore.exceptions import ClientError

from app.utils.resilience import get_env_var, with_retry

# Configuração de logging
logger = logging.getLogger(__name__)


class S3Connector:
    """Conector para MinIO/S3 com mecanismos de resiliência"""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: Optional[str] = None,
    ) -> None:
        """
        Inicializa o conector S3 com credenciais e endpoint

        Args:
            endpoint_url: URL do endpoint S3/MinIO
            access_key: Chave de acesso
            secret_key: Chave secreta
            region: Região (opcional para MinIO)
        """
        self.endpoint_url = endpoint_url or get_env_var(
            "MINIO_ENDPOINT", "http://minio:9000"
        )
        self.access_key = access_key or get_env_var("AWS_ACCESS_KEY_ID", "admin")
        self.secret_key = secret_key or get_env_var("AWS_SECRET_ACCESS_KEY", "admin123")
        self.region = region or get_env_var("AWS_REGION", "us-east-1")

        # Inicializa cliente e recurso
        self._init_clients()

    def _init_clients(self) -> None:
        """Inicializa os clientes boto3"""
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )

        self.s3_resource = boto3.resource(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )

    @with_retry(max_retries=5, initial_backoff=1.0, retryable_exceptions=(ClientError,))
    def create_bucket(self, bucket_name: str) -> None:
        """
        Cria um bucket S3 com retry em caso de falha

        Args:
            bucket_name: Nome do bucket a ser criado
        """
        try:
            if not self.bucket_exists(bucket_name):
                logger.info(f"Criando bucket: {bucket_name}")

                # Para MinIO podemos criar sem Location
                if self.endpoint_url and "minio" in self.endpoint_url.lower():
                    self.s3_client.create_bucket(Bucket=bucket_name)
                else:
                    # Para AWS S3 real
                    self.s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={"LocationConstraint": self.region},
                    )

                logger.info(f"Bucket {bucket_name} criado com sucesso")
            else:
                logger.info(f"Bucket {bucket_name} já existe")

        except ClientError as e:
            logger.error(f"Erro ao criar bucket {bucket_name}: {e}")
            raise

    @with_retry(max_retries=3, initial_backoff=1.0, retryable_exceptions=(ClientError,))
    def bucket_exists(self, bucket_name: str) -> bool:
        """
        Verifica se um bucket existe

        Args:
            bucket_name: Nome do bucket

        Returns:
            True se o bucket existir, False caso contrário
        """
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError:
            return False

    @with_retry(max_retries=3, initial_backoff=1.0, retryable_exceptions=(ClientError,))
    def upload_file(
        self,
        file_path: str,
        bucket_name: str,
        object_key: str,
        extra_args: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Faz upload de um arquivo para o bucket

        Args:
            file_path: Caminho do arquivo local
            bucket_name: Nome do bucket
            object_key: Chave do objeto no bucket
            extra_args: Argumentos adicionais (opcional)
        """
        try:
            logger.info(f"Uploading {file_path} para s3://{bucket_name}/{object_key}")

            # Cria o bucket se não existir
            if not self.bucket_exists(bucket_name):
                self.create_bucket(bucket_name)

            # Faz o upload
            self.s3_client.upload_file(
                Filename=file_path,
                Bucket=bucket_name,
                Key=object_key,
                ExtraArgs=extra_args,
            )

            logger.info(f"Upload completo: s3://{bucket_name}/{object_key}")

        except ClientError as e:
            logger.error(f"Erro ao fazer upload do arquivo {file_path}: {e}")
            raise

    @with_retry(max_retries=3, initial_backoff=1.0, retryable_exceptions=(ClientError,))
    def download_file(self, bucket_name: str, object_key: str, file_path: str) -> None:
        """
        Faz download de um arquivo do bucket

        Args:
            bucket_name: Nome do bucket
            object_key: Chave do objeto no bucket
            file_path: Caminho para salvar o arquivo
        """
        try:
            logger.info(f"Downloading s3://{bucket_name}/{object_key} para {file_path}")

            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Faz o download
            self.s3_client.download_file(
                Bucket=bucket_name, Key=object_key, Filename=file_path
            )

            logger.info(f"Download completo: {file_path}")

        except ClientError as e:
            logger.error(f"Erro ao fazer download do arquivo {object_key}: {e}")
            raise

    @with_retry(max_retries=3, initial_backoff=1.0, retryable_exceptions=(ClientError,))
    def list_objects(
        self, bucket_name: str, prefix: str = "", max_keys: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Lista objetos em um bucket

        Args:
            bucket_name: Nome do bucket
            prefix: Prefixo para filtrar objetos
            max_keys: Número máximo de chaves a retornar

        Returns:
            Lista de objetos
        """
        try:
            logger.info(f"Listando objetos em s3://{bucket_name}/{prefix}")

            response = self.s3_client.list_objects_v2(
                Bucket=bucket_name, Prefix=prefix, MaxKeys=max_keys
            )

            objects = []
            if "Contents" in response:
                objects = response["Contents"]

            return objects

        except ClientError as e:
            logger.error(f"Erro ao listar objetos em {bucket_name}/{prefix}: {e}")
            raise

    @with_retry(max_retries=3, initial_backoff=1.0, retryable_exceptions=(ClientError,))
    def upload_dataframe(
        self,
        df: pd.DataFrame,
        bucket_name: str,
        object_key: str,
        format: str = "parquet",
        **kwargs: Any,
    ) -> None:
        """
        Faz upload de um DataFrame para o bucket

        Args:
            df: DataFrame a ser salvo
            bucket_name: Nome do bucket
            object_key: Chave do objeto no bucket
            format: Formato do arquivo (parquet, csv, json)
            **kwargs: Argumentos adicionais para o método de salvamento
        """
        try:
            logger.info(
                f"Salvando DataFrame ({len(df)} linhas) para s3://{bucket_name}/{object_key}"
            )

            # Cria o bucket se não existir
            if not self.bucket_exists(bucket_name):
                self.create_bucket(bucket_name)

            # Cria um buffer em memória
            buffer = io.BytesIO()

            # Salva o DataFrame no formato especificado
            if format.lower() == "parquet":
                df.to_parquet(buffer, **kwargs)
            elif format.lower() == "csv":
                df.to_csv(buffer, **kwargs)
            elif format.lower() == "json":
                df.to_json(buffer, **kwargs)
            else:
                raise ValueError(f"Formato não suportado: {format}")

            # Reseta o ponteiro do buffer
            buffer.seek(0)

            # Faz o upload
            self.s3_client.upload_fileobj(
                Fileobj=buffer, Bucket=bucket_name, Key=object_key
            )

            logger.info(
                f"Upload do DataFrame completo: s3://{bucket_name}/{object_key}"
            )

        except (ClientError, ValueError) as e:
            logger.error(f"Erro ao fazer upload do DataFrame: {e}")
            raise

    @with_retry(max_retries=3, initial_backoff=1.0, retryable_exceptions=(ClientError,))
    def download_dataframe(
        self, bucket_name: str, object_key: str, format: str = "parquet", **kwargs: Any
    ) -> pd.DataFrame:
        """
        Faz download de um DataFrame do bucket

        Args:
            bucket_name: Nome do bucket
            object_key: Chave do objeto no bucket
            format: Formato do arquivo (parquet, csv, json)
            **kwargs: Argumentos adicionais para o método de leitura

        Returns:
            DataFrame carregado
        """
        try:
            logger.info(f"Carregando DataFrame de s3://{bucket_name}/{object_key}")

            # Cria um buffer em memória
            buffer = io.BytesIO()

            # Faz o download para o buffer
            self.s3_client.download_fileobj(
                Bucket=bucket_name, Key=object_key, Fileobj=buffer
            )

            # Reseta o ponteiro do buffer
            buffer.seek(0)

            # Carrega o DataFrame do formato especificado
            if format.lower() == "parquet":
                df = pd.read_parquet(buffer, **kwargs)
            elif format.lower() == "csv":
                df = pd.read_csv(buffer, **kwargs)
            elif format.lower() == "json":
                df = pd.read_json(buffer, **kwargs)
            else:
                raise ValueError(f"Formato não suportado: {format}")

            logger.info(f"DataFrame carregado com {len(df)} linhas")
            return df

        except (ClientError, ValueError) as e:
            logger.error(f"Erro ao carregar DataFrame: {e}")
            raise
