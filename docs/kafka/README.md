# Apache Kafka - Plataforma de Streaming

<div align="center">
  <img src="https://img.shields.io/badge/Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white" alt="Apache Kafka">
</div>

> Versão: 7.5.0

## O que é Apache Kafka?

Apache Kafka é uma plataforma distribuída de streaming de eventos de código aberto, capaz de lidar com trilhões de eventos por dia. Inicialmente concebido como um sistema de mensagens, o Kafka é frequentemente usado para construir pipelines de dados de streaming em tempo real e aplicações que se adaptam ou reagem a fluxos de dados.

## Componentes do Kafka no DataFlow Lab

Nosso ambiente inclui:

1. **Apache Kafka**: O sistema core de mensagens (v7.5.0)
2. **Apache ZooKeeper**: Serviço de coordenação (v7.5.0)
3. **Kafka UI**: Interface web moderna para gerenciamento (v0.7.1)

## Como Acessar

Os serviços Kafka estão disponíveis em:

- **Kafka Broker**: kafka:9092 (interno), localhost:29092 (externo)
- **Zookeeper**: zookeeper:2181
- **Kafka UI**: [http://localhost:8090](http://localhost:8090)

## Arquitetura do Kafka

A configuração do Kafka no DataFlow Lab consiste em:

```
                      ┌─────────────┐
                      │             │
                      │  ZooKeeper  │
                      │ (2181)      │
                      │             │
                      └──────┬──────┘
                             │
                             │
                      ┌──────▼──────┐
                      │             │
                      │    Kafka    │
                      │ (9092/29092)│
                      │             │
                      └──────┬──────┘
                             │
              ┌──────────────┴───────────────┐
              │                              │
        ┌─────▼─────┐                  ┌─────▼─────┐
        │           │                  │           │
        │ Producers │                  │ Consumers │
        │           │                  │           │
        └───────────┘                  └───────────┘
```

## Conceitos Básicos do Kafka

### Tópicos e Partições

Tópicos são categorias ou feeds de eventos nomeados onde os registros são publicados:

- **Tópicos**: Canais de mensagens identificados por nome
- **Partições**: Subdivisões dos tópicos para paralelismo
- **Offsets**: Posição sequencial de uma mensagem em uma partição

### Produtores e Consumidores

- **Produtores**: Publicam mensagens em tópicos
- **Consumidores**: Leem mensagens de tópicos
- **Grupos de Consumo**: Consumidores que trabalham juntos

## Uso com Python

### Produção de Mensagens

```python
from kafka import KafkaProducer
import json

# Configuração do produtor
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Enviar mensagem
producer.send('meu-topico', {'chave': 'valor', 'timestamp': '2025-05-14T12:00:00'})

# Garantir envio síncrono
producer.flush()
```

### Consumo de Mensagens

```python
from kafka import KafkaConsumer
import json

# Configuração do consumidor
consumer = KafkaConsumer(
    'meu-topico',
    bootstrap_servers=['kafka:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='meu-grupo-consumo',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Consumir mensagens
for message in consumer:
    print(f"Tópico: {message.topic}, Partição: {message.partition}")
    print(f"Offset: {message.offset}, Timestamp: {message.timestamp}")
    print(f"Chave: {message.key}, Valor: {message.value}")
    print("---")
```

### Consumo com Pyspark Structured Streaming

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType

# Configurar sessão Spark
spark = SparkSession.builder \
    .appName("KafkaStreaming") \
    .config("spark.sql.streaming.checkpointLocation", "s3a://bronze/checkpoints/kafka_stream") \
    .getOrCreate()

# Definir schema dos dados
schema = StructType([
    StructField("chave", StringType(), True),
    StructField("timestamp", StringType(), True)
])

# Ler stream do Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "meu-topico") \
    .option("startingOffsets", "earliest") \
    .load()

# Extrair valor das mensagens
parsed_df = df \
    .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
    .select(
        col("key"),
        from_json(col("value"), schema).alias("data")
    )

# Processar e gravar no Delta Lake (arquitetura medallion)
query = parsed_df \
    .writeStream \
    .outputMode("append") \
    .format("delta") \
    .option("checkpointLocation", "s3a://bronze/checkpoints/kafka_bronze") \
    .start("s3a://bronze/streaming/meu-topico")
```

## Administração via Kafka UI

A interface Kafka UI fornece:

- Visualização de tópicos e seus detalhes
- Monitoramento de grupos de consumidores
- Visualização e busca de mensagens
- Estatísticas de uso e performance

Para acessar: [http://localhost:8090](http://localhost:8090)

### Criação de Tópicos pela UI

1. Acesse a Kafka UI no navegador
2. Navegue até a seção "Topics"
3. Clique em "Add a Topic"
4. Preencha:
   - Nome do tópico
   - Número de partições
   - Fator de replicação
   - Configurações adicionais (se necessário)
5. Clique em "Create"

## Integração com Outros Serviços

### 1. Kafka + NiFi

O Apache NiFi pode ser configurado para:
- **Ler de Kafka**: Usando o processador `ConsumeKafka`
- **Escrever em Kafka**: Usando o processador `PublishKafka`

Exemplo de fluxo:
```
GetFile -> ExtractText -> PublishKafka
```

### 2. Kafka + Spark Streaming

O Kafka funciona perfeitamente com Spark Structured Streaming para:
- Processamento em tempo real
- Windowing e agregações
- ETL em streaming

### 3. Kafka + Python Microserviços

Para aplicações baseadas em microsserviços:

```python
# Consumidor em segundo plano como microserviço
import threading
from kafka import KafkaConsumer
import json

class KafkaService(threading.Thread):
    def __init__(self, topic, group_id):
        threading.Thread.__init__(self)
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=['kafka:9092'],
            auto_offset_reset='latest',
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.running = True
        
    def run(self):
        try:
            while self.running:
                for message in self.consumer:
                    self.process_message(message)
        finally:
            self.consumer.close()
    
    def process_message(self, message):
        # Lógica de processamento
        print(f"Processando: {message.value}")
    
    def stop(self):
        self.running = False
```

## Casos de Uso no DataFlow Lab

### 1. Ingestão de Dados em Streaming

Coleta contínua de dados de fontes externas para:
- Análises em tempo real
- Alimentação da camada Bronze do lakehouse
- Detecção de anomalias

### 2. Processamento Event-Driven

Reação a eventos em tempo real:
- Triggers para workflows do Prefect
- Alertas e notificações
- Atualizações de dashboards

### 3. Pipeline de Dados com Arquitetura Lambda

Combinação de:
- Processamento em lote (Spark batch)
- Processamento em tempo real (Kafka + Spark Streaming)

### 4. Sincronização entre Sistemas

- Propagação de alterações de dados entre sistemas
- Consistência eventual entre bancos de dados
- CDC (Change Data Capture)

## Configurações Avançadas

### Configuração do Broker

O broker Kafka está configurado com:

```yaml
KAFKA_BROKER_ID: 1
KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

### Persistência

Dados do Kafka são persistidos em volumes:
- `kafka-data`: Armazenamento dos logs e dados
- `zookeeper-data`: Armazenamento de dados do ZooKeeper
- `zookeeper-logs`: Logs do ZooKeeper

## Melhores Práticas

1. **Design de Tópicos**:
   - Manter baixo o número de partições por tópico (iniciar com 3-6)
   - Nomear tópicos de forma consistente (ex: `dominio.entidade.evento`)
   - Considerar retenção apropriada com base no caso de uso

2. **Produtores**:
   - Definir `acks=all` para dados críticos
   - Implementar retry com backoff para falhas de rede
   - Usar compressão para grandes volumes

3. **Consumidores**:
   - Gerenciar offsets manualmente para controle preciso
   - Dimensionar grupos de consumo com base nas partições
   - Implementar idempotência no processamento

4. **Monitoramento**:
   - Verificar lag de consumidores regularmente
   - Monitorar utilização dos brokers
   - Configurar alertas para partições sem líder

## Resolução de Problemas

| Problema                        | Solução                                      |
| ------------------------------- | -------------------------------------------- |
| Consumidor não recebe mensagens | Verifique grupo de consumo, offset e tópico  |
| Produtor falha ao enviar        | Verifique conectividade com o broker         |
| Alto lag de consumo             | Escale consumidores ou otimize processamento |
| Tópico não visível              | Verifique se o tópico realmente foi criado   |
| UI do Kafka inacessível         | Verifique se o container está ativo          |

## Recursos Adicionais

- [Documentação Oficial do Apache Kafka](https://kafka.apache.org/documentation/)
- [Confluent Developer](https://developer.confluent.io/)
- [Kafka Python Client](https://kafka-python.readthedocs.io/)
- [PySpark Structured Streaming com Kafka](https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html)
- [Kafka UI GitHub](https://github.com/provectuslabs/kafka-ui)