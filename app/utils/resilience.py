"""
Utilitários para melhorar a resiliência e conectividade entre serviços
"""

import logging
import os
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar, cast

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Tipo genérico para a função decorada
F = TypeVar("F", bound=Callable[..., Any])


def with_retry(
    max_retries: int = 5,
    initial_backoff: float = 1.0,
    max_backoff: float = 60.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: Tuple = (Exception,),
) -> Callable[[F], F]:
    """
    Decorator para adicionar retry a funções com backoff exponencial

    Args:
        max_retries: Número máximo de tentativas
        initial_backoff: Tempo de espera inicial em segundos
        max_backoff: Tempo máximo de espera em segundos
        backoff_factor: Fator multiplicativo para o backoff
        retryable_exceptions: Tupla de exceções que devem ser retentadas

    Returns:
        Decorator que adiciona retry à função
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            backoff = initial_backoff
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    wait_time = min(backoff, max_backoff)

                    logger.warning(
                        f"Tentativa {attempt + 1}/{max_retries} falhou para {func.__name__}: {str(e)}. "
                        f"Tentando novamente em {wait_time:.2f}s"
                    )

                    time.sleep(wait_time)
                    backoff *= backoff_factor

            logger.error(
                f"Todas as {max_retries} tentativas falharam para {func.__name__}"
            )
            if last_exception:
                raise last_exception

        return cast(F, wrapper)

    return decorator


def get_env_var(key: str, default: Optional[str] = None) -> str:
    """
    Obtém uma variável de ambiente com fallback para um valor padrão

    Args:
        key: Nome da variável de ambiente
        default: Valor padrão se a variável não existir

    Returns:
        Valor da variável de ambiente ou o valor padrão

    Raises:
        ValueError: Se a variável não existir e nenhum valor padrão for fornecido
    """
    value = os.environ.get(key, default)
    if value is None:
        raise ValueError(
            f"Variável de ambiente {key} não encontrada e nenhum valor padrão fornecido"
        )
    return value


def get_spark_configs() -> Dict[str, str]:
    """
    Obtém as configurações para o Spark com valores padrão resilientes

    Returns:
        Dicionário com configurações do Spark
    """
    return {
        # Configurações Delta Lake
        "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        # Configurações S3A/MinIO
        "spark.hadoop.fs.s3a.endpoint": get_env_var(
            "MINIO_ENDPOINT", "http://minio:9000"
        ),
        "spark.hadoop.fs.s3a.access.key": get_env_var("AWS_ACCESS_KEY_ID", "admin"),
        "spark.hadoop.fs.s3a.secret.key": get_env_var(
            "AWS_SECRET_ACCESS_KEY", "admin123"
        ),
        "spark.hadoop.fs.s3a.path.style.access": "true",
        "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
        # Configurações de resiliência e retry
        "spark.hadoop.fs.s3a.connection.maximum": "100",
        "spark.hadoop.fs.s3a.connection.timeout": "300000",
        "spark.hadoop.fs.s3a.connection.establish.timeout": "10000",
        "spark.hadoop.fs.s3a.attempts.maximum": "20",
        "spark.hadoop.fs.s3a.retry.interval": "1s",
        "spark.hadoop.fs.s3a.retry.limit": "20",
        # Otimizações de performance
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true",
        "spark.sql.shuffle.partitions": "200",
        "spark.default.parallelism": "100",
        # Configurações de checkpointing para maior resiliência
        "spark.checkpoint.compress": "true",
    }
