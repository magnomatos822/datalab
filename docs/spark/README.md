# Apache Spark e Delta Lake

<div align="center">
  <img src="https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white" alt="Apache Spark">
  <img src="https://img.shields.io/badge/Delta_Lake-00ADD8?style=for-the-badge&logo=delta&logoColor=white" alt="Delta Lake">
</div>

> Apache Spark: 3.5.5  
> Delta Lake: 3.3.1

## Apache Spark

### Visão Geral

Apache Spark é um sistema de computação em memória distribuído, unificado, rápido e escalável. No DataFlow Lab, o Spark é utilizado como motor principal de processamento de dados, fornecendo APIs para processamento em lote e streaming através de uma interface unificada.

### Arquitetura Spark no DataFlow Lab

A configuração do Spark no projeto segue uma arquitetura cliente-servidor:

```
                                 +------------------+
                                 |                  |
                                 |  Spark Master    |
                                 |  (porta: 7077)   |
                                 |                  |
                                 +--------|---------+
                                          |
                                          |
              +-------------------------+-+---------------------------+
              |                         |                             |
    +---------v----------+   +----------v---------+     +-------------v-------+
    |                    |   |                    |     |                     |
    |   Spark Worker     |   |      Cliente       |     |  Outros Serviços    |
    |   (porta: 8081)    |   |  (Notebooks, etc)  |     |  (Streamlit, etc)   |
    |                    |   |                    |     |                     |
    +--------------------+   +--------------------+     +---------------------+
```

### Componentes da Instalação

1. **Spark Master**:
   - Host: `spark-master`
   - Porta Web UI: `8080`
   - Porta Spark: `7077`

2. **Spark Worker**:
   - Host: `spark-worker`
   - Porta Web UI: `8081`

3. **Spark History Server**: (Configurável)
   - Logs de aplicações anteriores

4. **Bibliotecas Principais**:
   - PySpark Core: `pyspark==3.5.5`
   - Delta Lake: `delta-spark==3.3.1`
   - PyArrow: `pyarrow==19.0.1`

### Acesso e Utilização

#### Web UI

- **Spark Master**: [http://localhost:8080](http://localhost:8080)
- **Spark Worker**: [http://localhost:8081](http://localhost:8081)

#### Conexão via PySpark

Em um notebook Jupyter ou script Python:

```python
from pyspark.sql import SparkSession

# Criar sessão Spark com suporte a Delta Lake
spark = SparkSession.builder \
    .appName("MeuApp") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "admin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()
```

#### Conexão via Spark Submit

Para executar um job no cluster:

```bash
docker exec -it spark-master spark-submit \
  --master spark://spark-master:7077 \
  --conf "spark.hadoop.fs.s3a.endpoint=http://minio:9000" \
  --conf "spark.hadoop.fs.s3a.access.key=admin" \
  --conf "spark.hadoop.fs.s3a.secret.key=admin123" \
  --conf "spark.hadoop.fs.s3a.path.style.access=true" \
  --conf "spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem" \
  --packages io.delta:delta-core_2.12:3.3.1,org.apache.hadoop:hadoop-aws:3.3.4 \
  /opt/spark-apps/meu_script.py
```

## Delta Lake

### Visão Geral

Delta Lake é uma camada de armazenamento de código aberto que traz confiabilidade para data lakes. Ele fornece transações ACID, versionamento de dados (time travel) e gerenciamento de esquemas para o Apache Spark.

### Principais Recursos

1. **Transações ACID**
   - Operações atômicas e consistentes
   - Garantia que os leitores vejam uma visão consistente da tabela

2. **Time Travel**
   - Acesso a versões anteriores dos dados
   - Auditoria de alterações

3. **Schema Evolution**
   - Modificação flexível de esquemas
   - Validação automática de tipos

4. **Merge, Update e Delete**
   - Operações de atualização incremental
   - Upserts eficientes (MERGE INTO)

5. **Compactação de Arquivos**
   - OPTIMIZE para combinar pequenos arquivos
   - Z-ORDER para co-localização de dados relacionados

### Uso com PySpark

#### Escrita de Dados no Formato Delta

```python
# Criar ou modificar uma tabela Delta
df = spark.read.csv("s3a://bronze/raw_data_source1/table1/dataset.csv", header=True)
df.write.format("delta").save("s3a://silver/clean_data_domain1/table1")
```

#### Leitura de Dados Delta

```python
# Leitura padrão (versão mais recente)
df = spark.read.format("delta").load("s3a://silver/clean_data_domain1/table1")

# Time travel por versão
df_antiga = spark.read.format("delta").option("versionAsOf", 5).load("s3a://silver/clean_data_domain1/table1")

# Time travel por timestamp
df_ontem = spark.read.format("delta").option("timestampAsOf", "2025-05-13").load("s3a://silver/clean_data_domain1/table1")
```

#### Operações MERGE

```python
from delta.tables import DeltaTable

# Obter referência para tabela Delta existente
deltaTable = DeltaTable.forPath(spark, "s3a://silver/clean_data_domain1/table1")

# MERGE (upsert) com dataframe de atualizações
deltaTable.alias("target") \
  .merge(
    updates.alias("source"),
    "target.key = source.key"
  ) \
  .whenMatchedUpdate(set={
    "value": "source.value",
    "updated": "current_timestamp()"
  }) \
  .whenNotMatchedInsert(values={
    "key": "source.key",
    "value": "source.value",
    "updated": "current_timestamp()"
  }) \
  .execute()
```

#### Otimização de Tabelas

```python
# Compactar arquivos pequenos
spark.sql("OPTIMIZE delta.`s3a://silver/clean_data_domain1/table1`")

# Z-Order para co-localizar dados relacionados
spark.sql("OPTIMIZE delta.`s3a://silver/clean_data_domain1/table1` ZORDER BY (data, região)")

# Visualizar histórico da tabela
history = spark.sql("DESCRIBE HISTORY delta.`s3a://silver/clean_data_domain1/table1`")
history.show()
```

## Arquitetura Medallion no DataFlow Lab

O DataFlow Lab implementa a arquitetura Medallion, organizada em três camadas:

### 1. Bronze (Dados Brutos)

Dados brutos na forma original, sem modificações substanciais.

```python
raw_df = spark.read.json("s3a://raw-fonte/eventos")
raw_df.write.format("delta") \
    .mode("append") \
    .partitionBy("data") \
    .option("mergeSchema", "true") \
    .save("s3a://bronze/raw_data_source1/table1")
```

### 2. Silver (Dados Limpos)

Dados limpos, validados e transformados.

```python
bronze_df = spark.read.format("delta").load("s3a://bronze/raw_data_source1/table1")

# Aplicar transformações
clean_df = bronze_df.dropna() \
    .withColumn("data_proc", current_timestamp()) \
    .filter("valor > 0")

# Salvar na camada Silver
clean_df.write.format("delta") \
    .mode("overwrite") \
    .partitionBy("data") \
    .save("s3a://silver/clean_data_domain1/table1")
```

### 3. Gold (Dados para Consumo)

Dados agregados e modelados para consumo de negócio.

```python
silver_df = spark.read.format("delta").load("s3a://silver/clean_data_domain1/table1")

# Criar visões agregadas para consumo
aggregated_df = silver_df.groupBy("região", "data") \
    .agg(sum("valor").alias("total_valor"))

# Salvar na camada Gold
aggregated_df.write.format("delta") \
    .mode("overwrite") \
    .save("s3a://gold/analytics_domain1/dashboard1")
```

## Integrações

### 1. Spark com MinIO (S3)

O Spark está configurado para acessar dados no MinIO (compatível com S3):

```python
# Configuração para acesso ao MinIO já presente na sessão Spark
df = spark.read.format("delta").load("s3a://bronze/raw_data_source1/table1")
```

### 2. Spark com MLflow

Integração para rastreamento de experimentos ML:

```python
import mlflow.spark

# Registrar modelo Spark ML no MLflow
with mlflow.start_run():
    model = pipeline.fit(training_data)
    mlflow.spark.log_model(model, "spark-model")
```

### 3. Spark com Streamlit

Exposição de dados processados em dashboards:

```python
# No app Streamlit (app/app.py)
import streamlit as st
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
df = spark.read.format("delta").load("s3a://gold/analytics_domain1/dashboard1")
pandas_df = df.toPandas()

st.title("Dashboard de Análise")
st.dataframe(pandas_df)
st.line_chart(pandas_df.set_index("data")["total_valor"])
```

### 4. Spark Streaming com Kafka

Processamento em tempo real:

```python
# Consumir dados do Kafka
streaming_df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "kafka:9092") \
  .option("subscribe", "topico-entrada") \
  .load()

# Processar stream
query = streaming_df \
  .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
  .writeStream \
  .format("delta") \
  .outputMode("append") \
  .option("checkpointLocation", "s3a://bronze/checkpoints/kafka_bronze") \
  .start("s3a://bronze/streaming_data")
```

## Configurações Avançadas

### Ajuste de Performance

O Spark está configurado com estas otimizações:

1. **Alocação de Memória**:
   - Driver Memory: 1g
   - Executor Memory: 1g

2. **Concorrência**:
   - spark.default.parallelism: 8
   - spark.sql.shuffle.partitions: 8

3. **Cache e Spill**:
   - spark.memory.fraction: 0.8
   - spark.memory.storageFraction: 0.3

### Conectores Pré-instalados

1. **S3/MinIO**: hadoop-aws-3.3.4.jar
2. **Delta Lake**: delta-core_2.12-3.3.1.jar
3. **JDBC**: (vários drivers disponíveis)

## Monitoramento

O DataFlow Lab oferece várias maneiras de monitorar jobs Spark:

1. **Spark UI**:
   - Aplicações ativas: [http://localhost:8080](http://localhost:8080)
   - Detalhes de stages e tasks

2. **Log de Aplicações**:
   ```bash
   docker-compose logs spark-master
   ```

## Melhores Práticas

1. **Particionamento**:
   - Particione por colunas de filtro comum
   - Evite muitas partições pequenas

2. **Otimizações Delta**:
   - Execute OPTIMIZE regularmente
   - Use Z-ORDER para colunas frequentemente filtradas

3. **Gerenciamento de Recursos**:
   - Ajuste executor.memory com base no tamanho do worker
   - Configure partições baseado no número total de cores

4. **Monitoramento**:
   - Verifique a UI do Spark para gargalos
   - Observe métricas como spill, shuffle e GC

## Resolução de Problemas

| Problema | Possível Solução |
|----------|-----------------|
| Out of Memory | Aumente driver/executor memory ou particione melhor os dados |
| Lentidão em joins | Use broadcast para tabelas pequenas; verifique particionamento |
| Arquivos muito pequenos | Execute OPTIMIZE nas tabelas Delta |
| Conexão S3/MinIO falha | Verifique credenciais e endpoint no arquivo .env |
| Job travado | Verifique logs do executor e possíveis deadlocks |

## Recursos e Referências

- [Documentação do Apache Spark](https://spark.apache.org/docs/3.5.5/)
- [Documentação do Delta Lake](https://docs.delta.io/3.3.1/index.html)
- [Guia de Tuning do Spark](https://spark.apache.org/docs/latest/tuning.html)
- [Exemplos no DataFlow Lab](../../app/medallion_example.py)
