# Kafka no DataLab

Este documento apresenta o serviço Apache Kafka que foi adicionado ao ambiente DataLab.

## Sobre o Apache Kafka

O Apache Kafka é uma plataforma de streaming distribuído que permite publicar, assinar, armazenar e processar fluxos de eventos em tempo real. É ideal para pipelines de dados e aplicações que exigem alta capacidade de processamento de streams de dados.

## Componentes Implementados

No ambiente DataLab, foram incluídos os seguintes componentes:

1. **ZooKeeper** - Serviço necessário para gerenciar o cluster Kafka
2. **Kafka Broker** - O serviço principal do Apache Kafka
3. **Kafka UI** - Interface gráfica moderna para gerenciar o Kafka

## Portas e Acessos

- **ZooKeeper**: Porta 2181
- **Kafka Broker**: 
  - Porta 9092 (comunicação interna)
  - Porta 29092 (acesso externo via localhost)
- **Kafka UI**: Porta 8090 (http://localhost:8090)

## Usando o Kafka UI

A interface do Kafka permite:

1. Visualizar tópicos, partições e mensagens
2. Criar e excluir tópicos
3. Produzir e consumir mensagens para teste
4. Monitorar grupos de consumidores
5. Visualizar métricas do broker

Para acessar a UI, abra um navegador e acesse:
```
http://localhost:8090
```

## Integração com outros componentes do DataLab

### Spark
Para processar streams do Kafka usando o Spark, você pode usar o Spark Structured Streaming ou o Spark Streaming. No seu código Python dentro do Spark:

```python
# Exemplo com Spark Structured Streaming
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "meu-topico") \
    .load()

# Processamento dos dados...
```

### NiFi
Você pode usar os processores Kafka do NiFi para:
- PublishKafka: Enviar dados para o Kafka
- ConsumeKafka: Receber dados do Kafka

### Prefect
Para integrar com fluxos do Prefect:

```python
from prefect import flow, task
from kafka import KafkaProducer, KafkaConsumer

@task
def enviar_para_kafka(dados):
    producer = KafkaProducer(bootstrap_servers=['kafka:9092'])
    producer.send('meu-topico', dados.encode())
    producer.flush()
    
@flow
def meu_fluxo():
    # Código do fluxo
    dados = "Mensagem de teste"
    enviar_para_kafka(dados)
```

## Volumes persistentes

Os dados do Kafka e ZooKeeper são armazenados em volumes Docker para garantir persistência:
- `zookeeper-data`: Dados do ZooKeeper
- `zookeeper-logs`: Logs do ZooKeeper
- `kafka-data`: Dados e logs do Kafka

## Configuração avançada

Para customizar as configurações do Kafka, edite as variáveis de ambiente no arquivo `docker-compose.yml`. Algumas configurações importantes:

- `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR`: Fator de replicação para tópicos internos
- `KAFKA_TRANSACTION_STATE_LOG_MIN_ISR`: Número mínimo de réplicas sincronizadas
- `KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR`: Fator de replicação para logs de transações

Para um ambiente de produção, recomenda-se aumentar o número de brokers e configurar adequadamente os fatores de replicação.