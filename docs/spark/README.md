# Apache Spark e Delta Lake no DataFlow Lab

## Visão Geral

O Apache Spark é um framework de processamento distribuído que permite o processamento de grandes volumes de dados de forma rápida e eficiente. No DataFlow Lab, o Spark é integrado com o Delta Lake para fornecer transações ACID, viagem no tempo (time travel) e outras funcionalidades críticas para uma arquitetura de dados moderna.

Última atualização: **13 de maio de 2025**

## Apache Spark

### Componentes

- **Spark Core**: Engine de processamento distribuído
- **Spark SQL**: Processamento de dados estruturados
- **Spark Streaming**: Processamento de streaming em tempo real
- **MLlib**: Biblioteca de machine learning
- **GraphX**: Processamento de grafos

### Configuração no DataFlow Lab

No DataFlow Lab, o Spark é configurado como:

- **Master**: Nó principal que gerencia os workers
- **Worker**: Nós que executam o processamento efetivo
- **History Server**: Para visualização de jobs históricos
- **Versão**: Apache Spark 3.5.5
- **Modo de execução**: Standalone

### Acessando as UIs do Spark

- **Master UI**: [http://localhost:8080](http://localhost:8080)
- **Worker UI**: [http://localhost:8081](http://localhost:8081)
- **Autenticação**: Não há autenticação configurada para o ambiente de desenvolvimento

## Delta Lake

### O que é Delta Lake?

Delta Lake é uma camada de armazenamento de código aberto que traz confiabilidade ao data lake. Ele fornece transações ACID, esquematização, evolução de esquema e unificação de processamento em lote e streaming.

### Características Principais

1. **Transações ACID**: Garante consistência de dados mesmo em caso de falhas
2. **Time Travel**: Acesso a versões anteriores dos dados
3. **Schema Enforcement**: Previne dados inválidos
4. **Schema Evolution**: Permite alterações no esquema ao longo do tempo
5. **Merge, Update, Delete**: Operações de atualização que não são possíveis em formatos como Parquet
6. **Indexação Z-Order**: Otimiza a performance de consultas
7. **Compactação de Arquivos Pequenos**: Melhora a performance de leitura

### Uso com a Arquitetura Medallion

Delta Lake é utilizado em todas as camadas da arquitetura Medallion:

1. **Bronze**: Armazena dados brutos com garantias ACID
2. **Silver**: Armazena dados limpos e transformados
3. **Gold**: Armazena dados agregados para análise

### Operações Comuns com Delta Lake

#### Leitura de dados

```python
# Leitura simples
df = spark.read.format("delta").load("s3a://bronze/dataset")

# Leitura com time travel (versão específica)
df_v1 = spark.read.format("delta").option("versionAsOf", 1).load("s3a://bronze/dataset")

# Leitura com time travel (timestamp)
df_ts = spark.read.format("delta").option("timestampAsOf", "2025-05-10 12:00:00").load("s3a://bronze/dataset")
```

#### Escrita de dados

```python
# Escrita simples
df.write.format("delta").save("s3a://silver/dataset")

# Escrita com modo
df.write.format("delta").mode("overwrite").save("s3a://silver/dataset")

# Escrita com particionamento
df.write.format("delta").partitionBy("date").save("s3a://silver/dataset")
```

#### Operações Merge

```python
from delta.tables import DeltaTable

# Carregar tabela existente
delta_table = DeltaTable.forPath(spark, "s3a://silver/dataset")

# Executar merge (upsert)
delta_table.alias("target").merge(
    source = updates_df.alias("source"),
    condition = "target.key = source.key"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

#### Otimização de Tabelas

```python
# Compactação de arquivos pequenos
spark.sql(f"OPTIMIZE delta.`s3a://silver/dataset`")

# Z-Ordering para otimizar consultas
spark.sql(f"OPTIMIZE delta.`s3a://silver/dataset` ZORDER BY (date, customer_id)")
```

#### Gerenciamento de Histórico

```python
# Visualizar histórico de versões
spark.sql(f"DESCRIBE HISTORY delta.`s3a://silver/dataset`").show()

# Restaurar versão anterior
spark.sql(f"RESTORE delta.`s3a://silver/dataset` VERSION AS OF 5")

# Limpar histórico antigo (vacuum)
spark.sql(f"VACUUM delta.`s3a://silver/dataset` RETAIN 30 DAYS")
```

### Melhorias de Desempenho

Para otimizar o desempenho do Delta Lake:

1. **Particionamento adequado**: Particione os dados com base nos padrões de consulta
2. **Z-Order**: Use Z-Order para colunas frequentemente filtradas
3. **Vacuum regularmente**: Para evitar acúmulo de arquivos antigos
4. **Optimize**: Execute regularmente para compactar arquivos pequenos
5. **Caching**: Use cache para tabelas frequentemente acessadas

## Integrando Spark com MinIO

O Spark é configurado para trabalhar diretamente com o MinIO através do conector S3A:

```python
spark = SparkSession.builder \
    .appName("MeuApp") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "admin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()
```

## Monitoramento e Logs

Para visualizar logs e monitorar aplicações Spark:

1. **Spark UI**: Acesse a UI do Spark Master para ver aplicações em execução e completadas
2. **Log Files**: Os logs estão disponíveis em `/data/spark/logs` no container
3. **Driver Logs**: Para aplicações específicas, veja os logs do driver em `/data/spark/work-dir`

## Troubleshooting

Problemas comuns e soluções:

1. **Out of Memory**: Aumente a memória do worker ou do driver nas configurações
2. **Executors Lost**: Verifique se há problemas de recursos no nó worker
3. **S3A Connection Issues**: Verifique as credenciais e disponibilidade do MinIO
4. **Delta Lake Errors**: Verifique compatibilidade de versões e configurações

## Referências

- [Documentação Apache Spark](https://spark.apache.org/docs/latest/)
- [Documentação Delta Lake](https://docs.delta.io/latest/)
- [Delta Lake GitHub](https://github.com/delta-io/delta)
- [MinIO Integration](https://docs.min.io/docs/how-to-use-spark-with-minio.html)
