# Prefect - Orquestração de Fluxos de Dados

<div align="center">
  <img src="https://img.shields.io/badge/Prefect-024DFD?style=for-the-badge&logo=prefect&logoColor=white" alt="Prefect">
</div>

> Versão: 3.4.1

## O que é o Prefect?

Prefect é uma moderna plataforma de orquestração de fluxos de trabalho para coordenar pipelines de dados e ML. Diferente de orquestradores tradicionais, o Prefect traz observabilidade, tratamento de erros avançado, escalonamento dinâmico, e uma abordagem orientada a eventos, perfeita para fluxos de dados complexos.

## Características do Prefect

- **Execução Dinâmica**: Fluxos que se adaptam às entradas e condições
- **Tratamento Robusto de Falhas**: Políticas de retry, exceções personalizadas
- **Observabilidade**: Monitoramento e logs detalhados
- **Orquestração Moderna**: Baseada em funções Python nativas (Taskflow API)
- **Escalonável**: Da execução local à distribuída

## Como Acessar

O Prefect está disponível em:

- **URL**: http://localhost:4200
- **API URL**: http://localhost:4200/api (para clientes)

## Configuração no DataLab

No DataFlow Lab, o Prefect está configurado como:

- **Backend**: SQLite (para desenvolvimento)
- **Storage**: Sistema de arquivos local (data/prefect)
- **Volumes mapeados**:
  - Dados: `./data:/opt/prefect/data`
  - Fluxos: `./flows:/opt/prefect/flows`
  - Configuração: `./data/prefect:/opt/prefect`

## Conceitos Básicos

### 1. Fluxos (Flows)

Fluxos são a unidade principal de trabalho no Prefect. Um fluxo é uma coleção de tarefas organizadas para atingir um objetivo específico:

```python
from prefect import flow, task

@task
def extrair():
    # Extrai dados da fonte
    return dados

@task
def transformar(dados):
    # Transforma os dados
    return dados_transformados

@task
def carregar(dados):
    # Carrega os dados no destino
    return "Sucesso!"

@flow(name="ETL Simples")
def etl_pipeline():
    dados = extrair()
    dados_transformados = transformar(dados)
    resultado = carregar(dados_transformados)
    return resultado

if __name__ == "__main__":
    etl_pipeline()
```

### 2. Tarefas (Tasks)

Tarefas são as unidades atômicas de trabalho dentro de um fluxo:

- Podem depender umas das outras
- Têm estado (executando, concluído, falha)
- Suportam retentativas e timeout
- Podem ser paralelizadas

### 3. Deployments

Deployments permitem agendar e acionar fluxos a partir da interface:

```python
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule

# Criar deployment
deployment = Deployment.build_from_flow(
    flow=etl_pipeline,
    name="etl-agendado",
    schedule=CronSchedule(cron="0 0 * * *"),  # Diariamente à meia-noite
    tags=["produção", "etl"]
)

# Aplicar deployment
if __name__ == "__main__":
    deployment.apply()
```

## Exemplos Práticos

### Arquitetura Medallion com Prefect

Exemplo de como implementar a arquitetura Medallion usando Prefect:

```python
from prefect import flow, task
from pyspark.sql import SparkSession
import datetime como dt

@task(name="Inicializar Spark")
def iniciar_spark():
    # Configurar sessão Spark com Delta Lake
    spark = SparkSession.builder \
        .appName("Medallion-Pipeline") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "admin") \
        .config("spark.hadoop.fs.s3a.secret.key", "admin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .getOrCreate()
    return spark

@task(name="Bronze: Ingestão")
def bronze_layer(spark, fonte, destino):
    # Carregar dados brutos
    df = spark.read.json(fonte)
    
    # Adicionar metadados
    df = df.withColumn("data_ingestao", lit(dt.datetime.now().isoformat()))
    
    # Salvar na camada Bronze
    df.write.format("delta") \
        .mode("append") \
        .option("mergeSchema", "true") \
        .save(destino)
    
    return destino

@task(name="Silver: Limpeza")
def silver_layer(spark, fonte_bronze, destino_silver):
    # Ler dados da Bronze
    df = spark.read.format("delta").load(fonte_bronze)
    
    # Aplicar transformações
    df_clean = df.dropna() \
        .filter("valor > 0") \
        .withColumn("data_processamento", lit(dt.datetime.now().isoformat()))
    
    # Salvar na Silver
    df_clean.write.format("delta") \
        .mode("overwrite") \
        .partitionBy("data") \
        .save(destino_silver)
    
    return destino_silver

@task(name="Gold: Agregações")
def gold_layer(spark, fonte_silver, destino_gold):
    # Ler dados da Silver
    df = spark.read.format("delta").load(fonte_silver)
    
    # Criar visão agregada
    df_agg = df.groupBy("regiao", "data") \
        .agg(sum("valor").alias("total_valor"))
    
    # Salvar na Gold
    df_agg.write.format("delta") \
        .mode("overwrite") \
        .save(destino_gold)
    
    return destino_gold

@flow(name="Pipeline Medallion")
def medallion_pipeline(fonte="s3a://raw/eventos"):
    spark = iniciar_spark()
    
    bronze_path = bronze_layer(
        spark, 
        fonte, 
        "s3a://bronze/raw_data_source1/eventos"
    )
    
    silver_path = silver_layer(
        spark, 
        bronze_path, 
        "s3a://silver/clean_data_domain1/eventos"
    )
    
    gold_path = gold_layer(
        spark, 
        silver_path, 
        "s3a://gold/analytics_domain1/eventos_por_regiao"
    )
    
    return {"bronze": bronze_path, "silver": silver_path, "gold": gold_path}

# Criar deployment
if __name__ == "__main__":
    from prefect.deployments import Deployment
    from prefect.server.schemas.schedules import IntervalSchedule
    from datetime import timedelta
    
    deployment = Deployment.build_from_flow(
        flow=medallion_pipeline,
        name="pipeline-medallion-diario",
        schedule=IntervalSchedule(interval=timedelta(days=1)),
        tags=["medalion", "etl", "producao"]
    )
    
    deployment.apply()
```

### Notificações e Alertas

```python
from prefect import flow
from prefect.blocks.notifications import SlackWebhook

# Configurar notificação Slack
slack_webhook_block = SlackWebhook.load("nome-do-block")

@flow(name="Flow com Notificações")
def flow_com_notificacao():
    try:
        # Lógica do fluxo
        resultado = processar_dados()
        
        # Notificação de sucesso
        slack_webhook_block.notify(f"Fluxo concluído com sucesso: {resultado}")
        
        return resultado
    except Exception as e:
        # Notificação de falha
        slack_webhook_block.notify(f"Falha no fluxo: {e}")
        raise
```

### Paralelismo e Concorrência

```python
from prefect import flow, task
import asyncio

@task
def processar_chunk(chunk):
    # Processa um pedaço dos dados
    return len(chunk)

@flow(name="Processamento Paralelo")
async def processar_em_paralelo(dados):
    # Dividir dados em chunks
    chunks = [dados[i:i+100] for i in range(0, len(dados), 100)]
    
    # Processar chunks em paralelo (até 5 ao mesmo tempo)
    resultados = await asyncio.gather(*[processar_chunk.submit(chunk) for chunk in chunks])
    
    return sum(resultados)
```

## Integração com Outros Serviços

### 1. Prefect + Spark

```python
@task(name="Executar Job Spark")
def executar_spark_job(app_name, data_path):
    # Configurar sessão Spark
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .getOrCreate()
    
    # Processar dados
    df = spark.read.parquet(data_path)
    resultado = df.groupBy("categoria").count()
    
    return resultado.count()
```

### 2. Prefect + MLflow

```python
from prefect import task, flow
import mlflow

@task(name="Treinar Modelo")
def treinar_modelo(params, data_path):
    # Configurar MLflow
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("meu-experimento")
    
    # Treinar com tracking
    with mlflow.start_run():
        mlflow.log_params(params)
        
        # Lógica de treino
        model = treinar(params, data_path)
        
        # Log métricas e modelo
        mlflow.log_metrics({"acuracia": model.acuracia})
        mlflow.sklearn.log_model(model, "modelo")
        
        return model.acuracia

@flow(name="Fluxo de ML")
def pipeline_ml(params={"alpha": 0.5}):
    acuracia = treinar_modelo(params, "s3a://silver/dados_treino")
    return acuracia
```

### 3. Prefect + Kafka

```python
from prefect import task, flow
from kafka import KafkaConsumer, KafkaProducer
import json

@task(name="Consumir Mensagens Kafka")
def consumir_kafka(topico, limite=100):
    mensagens = []
    consumer = KafkaConsumer(
        topico,
        bootstrap_servers=["kafka:9092"],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        consumer_timeout_ms=10000  # 10 segundos
    )
    
    for i, mensagem in enumerate(consumer):
        if i >= limite:
            break
        mensagens.append(mensagem.value)
    
    return mensagens

@task(name="Processar Mensagens")
def processar_mensagens(mensagens):
    # Processar as mensagens
    return [processar(msg) for msg in mensagens]

@task(name="Publicar Resultados")
def publicar_resultados(resultados, topico):
    producer = KafkaProducer(
        bootstrap_servers=["kafka:9092"],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    for resultado in resultados:
        producer.send(topico, value=resultado)
    
    producer.flush()
    return len(resultados)

@flow(name="Pipeline Kafka")
def pipeline_kafka(topico_entrada, topico_saida, limite=100):
    mensagens = consumir_kafka(topico_entrada, limite)
    resultados = processar_mensagens(mensagens)
    total_publicados = publicar_resultados(resultados, topico_saida)
    return total_publicados
```

## Monitoramento e Observabilidade

### Dashboard do Prefect

O Dashboard do Prefect oferece:

- Visualização de fluxos em execução
- Histórico de execuções
- Logs detalhados
- Estado das tarefas
- Agendamento e gatilhos

### Logs e Alertas

Para configurar logs específicos:

```python
from prefect import flow, task
import logging

# Configurar logger
logger = logging.getLogger("meu-flow")
logger.setLevel(logging.INFO)

@task(name="Tarefa com Logs")
def tarefa_logging():
    logger.info("Iniciando processamento")
    try:
        # Lógica
        logger.info("Processamento concluído")
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        raise
```

## Melhores Práticas

1. **Reutilização de Tarefas**:
   - Crie tarefas genéricas para operações comuns
   - Use parâmetros para flexibilidade

2. **Tratamento de Erros**:
   - Configure políticas de retry para tarefas sensíveis
   - Use exceções personalizadas

3. **Agendamento Eficiente**:
   - Prefira intervalos maiores quando possível
   - Use cron para agendamentos precisos

4. **Otimizando Performance**:
   - Particione grandes conjuntos de dados
   - Use dask ou ray para processamento paralelo intenso

5. **Métricas e Telemetria**:
   - Log métricas importantes em cada execução
   - Configure health checks para pipelines críticos

## Resolução de Problemas

| Problema                      | Solução                                                            |
| ----------------------------- | ------------------------------------------------------------------ |
| Flow travado                  | Verifique os logs e o status na UI do Prefect                      |
| Erros de conexão              | Confirme que o servidor Prefect está acessível                     |
| Falhas em tarefas específicas | Use a opção de retry e verifique as dependências                   |
| Problemas de permissão        | Verifique permissões nos volumes compartilhados                    |
| Prefect UI inacessível        | Verifique se o container está rodando: `docker-compose ps prefect` |

## Recursos Adicionais

- [Documentação Oficial do Prefect](https://docs.prefect.io/)
- [Prefect Discourse](https://discourse.prefect.io/)
- [Exemplos no GitHub do Prefect](https://github.com/PrefectHQ/prefect-recipes)
- [Integração Prefect com Delta Lake](https://github.com/PrefectHQ/prefect-recipes/tree/main/nlp-recipes)
- [Exemplos DataFlow Lab](../../app/medallion_prefect_flow.py)
