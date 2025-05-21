"""
Utilitários para trabalhar com Kafka de forma resiliente
"""

import json
import logging
from typing import Any, Dict, List, Optional

from confluent_kafka import Consumer, KafkaException, Producer
from confluent_kafka.admin import AdminClient, NewTopic

from app.utils.resilience import get_env_var, with_retry

# Configuração de logging
logger = logging.getLogger(__name__)


def get_kafka_config(is_consumer: bool = False) -> Dict[str, str]:
    """
    Obtém a configuração para o Kafka com parâmetros de resiliência

    Args:
        is_consumer: Se True, adiciona configurações específicas para consumidores

    Returns:
        Dicionário com configurações do Kafka
    """
    config = {
        "bootstrap.servers": get_env_var("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        # Configurações de resiliência
        "socket.timeout.ms": "30000",
        "request.timeout.ms": "30000",
        "reconnect.backoff.max.ms": "10000",
        "reconnect.backoff.ms": "1000",
        "retry.backoff.ms": "1000",
    }

    if is_consumer:
        consumer_config = {
            "group.id": get_env_var("KAFKA_CONSUMER_GROUP_ID", "datalab-consumer"),
            "auto.offset.reset": "earliest",
            "enable.auto.commit": "false",
            "max.poll.interval.ms": "300000",  # 5 minutos
            "session.timeout.ms": "60000",  # 1 minuto
        }
        config.update(consumer_config)

    return config


@with_retry(
    max_retries=5,
    initial_backoff=1.0,
    max_backoff=30.0,
    retryable_exceptions=(KafkaException,),
)
def create_topic(
    topic_name: str, num_partitions: int = 3, replication_factor: int = 1
) -> None:
    """
    Cria um tópico Kafka com retry em caso de falha

    Args:
        topic_name: Nome do tópico a ser criado
        num_partitions: Número de partições
        replication_factor: Fator de replicação
    """
    logger.info(f"Criando tópico Kafka: {topic_name}")

    admin_client = AdminClient(get_kafka_config())

    # Verifica se o tópico já existe
    metadata = admin_client.list_topics(timeout=10)

    if topic_name in metadata.topics:
        logger.info(f"Tópico {topic_name} já existe")
        return

    # Cria o tópico
    topic = NewTopic(
        topic_name, num_partitions=num_partitions, replication_factor=replication_factor
    )

    fs = admin_client.create_topics([topic])

    # Aguarda a conclusão
    for topic, f in fs.items():
        try:
            f.result()  # Bloqueia até a conclusão
            logger.info(f"Tópico {topic} criado com sucesso")
        except Exception as e:
            logger.error(f"Falha ao criar o tópico {topic}: {e}")
            raise


class ResilientProducer:
    """Produtor Kafka com mecanismos de resiliência"""

    def __init__(self) -> None:
        """Inicializa o produtor resiliente"""
        self.config = get_kafka_config()
        self.producer = Producer(self.config)

    @with_retry(max_retries=3, initial_backoff=1.0)
    def produce(self, topic: str, key: Optional[str], value: Dict[str, Any]) -> None:
        """
        Envia uma mensagem para um tópico Kafka com retry

        Args:
            topic: Nome do tópico
            key: Chave da mensagem (opcional)
            value: Valor da mensagem (será serializado para JSON)
        """
        try:
            # Serializa o valor para JSON
            serialized_value = json.dumps(value).encode("utf-8")

            # Serializa a chave se presente
            serialized_key = key.encode("utf-8") if key else None

            # Callback para verificar se houve erro
            def delivery_callback(err, msg):
                if err:
                    logger.error(f"Erro ao entregar mensagem: {err}")
                    raise KafkaException(str(err))
                else:
                    logger.debug(
                        f"Mensagem entregue: {msg.topic()} [{msg.partition()}] @ {msg.offset()}"
                    )

            # Produz a mensagem
            self.producer.produce(
                topic=topic,
                key=serialized_key,
                value=serialized_value,
                callback=delivery_callback,
            )

            # Espera que todas as mensagens sejam entregues
            self.producer.flush()

        except Exception as e:
            logger.error(f"Erro ao produzir mensagem: {e}")
            raise


class ResilientConsumer:
    """Consumidor Kafka com mecanismos de resiliência"""

    def __init__(self, topics: List[str], group_id: Optional[str] = None) -> None:
        """
        Inicializa o consumidor resiliente

        Args:
            topics: Lista de tópicos para se inscrever
            group_id: ID do grupo de consumidores (opcional)
        """
        self.config = get_kafka_config(is_consumer=True)

        # Sobrescreve o group_id se fornecido
        if group_id:
            self.config["group.id"] = group_id

        self.consumer = Consumer(self.config)
        self.consumer.subscribe(topics)

    @with_retry(
        max_retries=3, initial_backoff=1.0, retryable_exceptions=(KafkaException,)
    )
    def consume(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        Consome uma mensagem dos tópicos inscritos

        Args:
            timeout: Tempo máximo de espera em segundos

        Returns:
            Mensagem consumida ou None se não houver mensagem
        """
        try:
            # Tenta consumir uma mensagem
            msg = self.consumer.poll(timeout)

            if msg is None:
                return None

            if msg.error():
                logger.error(f"Erro ao consumir mensagem: {msg.error()}")
                raise KafkaException(msg.error())

            # Decodifica a mensagem
            try:
                value = json.loads(msg.value().decode("utf-8"))

                # Cria um objeto com metadados e valor
                result = {
                    "topic": msg.topic(),
                    "partition": msg.partition(),
                    "offset": msg.offset(),
                    "timestamp": msg.timestamp(),
                    "key": msg.key().decode("utf-8") if msg.key() else None,
                    "value": value,
                }

                return result

            except json.JSONDecodeError as e:
                logger.error(f"Erro ao decodificar mensagem JSON: {e}")
                raise

        except Exception as e:
            logger.error(f"Erro ao consumir mensagem: {e}")
            raise

    def close(self) -> None:
        """Fecha o consumidor"""
        self.consumer.close()

    def __enter__(self) -> "ResilientConsumer":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
