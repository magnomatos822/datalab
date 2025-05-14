# Prefect no DataFlow Lab

## Visão Geral

[Prefect](https://www.prefect.io/) é uma plataforma moderna de orquestração de fluxos de trabalho para dados. No DataFlow Lab, o Prefect é utilizado para orquestrar, programar e monitorar os fluxos de transformação de dados entre as camadas Bronze, Silver e Gold do nosso Data Lakehouse.

Última atualização: **13 de maio de 2025**

## Componentes Principais

- **Flows**: Unidades fundamentais de trabalho no Prefect, representam sua lógica de negócios
- **Tasks**: Unidades atômicas dentro de um flow, realizando operações específicas
- **Schedules**: Programação de execução de flows em intervalos definidos
- **UI Web**: Interface para visualizar, monitorar e gerenciar execuções
- **API**: Permite integração com outras ferramentas e sistemas
- **Work Queues**: Gerenciamento e distribuição de trabalho entre workers
- **Block Storage**: Armazenamento de configurações e segredos de forma segura

## Como Utilizar

### Acessando a Interface Web do Prefect

1. Após iniciar o ambiente com `docker-compose up -d`, acesse:
   - URL: http://localhost:4200
   - Usuário: Não há autenticação por padrão na instalação local
   - Configuração de banco de dados: SQLite - `/opt/prefect/prefect.db`
   - Variáveis de ambiente:
     - PREFECT_UI_API_URL=http://localhost:4200/api
     - PREFECT_API_URL=http://localhost:4200/api

### Criando um Flow Básico

Aqui está um exemplo de como criar um flow Prefect básico para processar dados entre as camadas Bronze e Silver:

```python
from prefect import flow, task
from pyspark.sql import SparkSession
from datetime import datetime
import os

@task(name="Iniciar Spark Session")
def start_spark_session():
    """Inicializa e retorna uma sessão Spark"""
    spark = (SparkSession.builder
             .appName("Bronze-to-Silver")
             .config("spark.jars.packages", "io.delta:delta-core_2.12:2.3.0")
             .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
             .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
             .getOrCreate())
    return spark

@task(name="Ler da Camada Bronze")
def read_from_bronze(spark, source_table):
    """Lê dados da camada Bronze"""
    bronze_path = f"s3a://bronze/{source_table}"
    df = spark.read.format("delta").load(bronze_path)
    return df

@task(name="Aplicar Transformações")
def apply_transformations(df):
    """Aplica transformações nos dados"""
    # Exemplo de transformações simples
    from pyspark.sql.functions import col, to_date
    
    df_transformed = (df
                     .drop("_airbyte_ab_id", "_airbyte_emitted_at")
                     .withColumn("created_date", to_date(col("created_at")))
                     .filter(col("status") != "deleted"))
    
    return df_transformed

@task(name="Escrever na Camada Silver")
def write_to_silver(df, target_table):
    """Escreve dados transformados na camada Silver"""
    silver_path = f"s3a://silver/{target_table}"
    
    (df.write
       .format("delta")
       .mode("overwrite")
       .save(silver_path))
    
    return silver_path

@flow(name="Bronze-to-Silver ETL")
def bronze_to_silver_flow(source_table: str, target_table: str):
    """Flow principal para processar dados de Bronze para Silver"""
    # Execute tasks em sequência
    spark = start_spark_session()
    raw_data = read_from_bronze(spark, source_table)
    transformed_data = apply_transformations(raw_data)
    silver_path = write_to_silver(transformed_data, target_table)
    
    # Encerra a sessão Spark
    spark.stop()
    
    return {"status": "success", "silver_path": silver_path}

# Exemplo de uso
if __name__ == "__main__":
    bronze_to_silver_flow("vendas", "vendas_processed")
```

### Registrando e Programando Flows

Para executar seus flows automaticamente em uma programação:

```python
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule
from bronze_to_silver import bronze_to_silver_flow

# Cria um deployment com agendamento
deployment = Deployment.build_from_flow(
    flow=bronze_to_silver_flow,
    name="Bronze-to-Silver-Daily",
    parameters={"source_table": "vendas", "target_table": "vendas_processed"},
    schedule=CronSchedule(cron="0 2 * * *"),  # Executa às 2h da manhã todos os dias
    tags=["etl", "bronze-to-silver"]
)

# Aplica o deployment
if __name__ == "__main__":
    deployment.apply()
```

### Integração dos Fluxos Medallion no Prefect

Para implementar o padrão Medallion completo no Prefect, crie fluxos para cada transição entre camadas:

1. **Airbyte → Bronze**: Orquestrando extrações do Airbyte para a camada Bronze
2. **Bronze → Silver**: Aplicando limpeza, validação e transformações iniciais
3. **Silver → Gold**: Criando visões agregadas e modelos para análise de negócios

## Integração com MLflow

O Prefect pode ser facilmente integrado com MLflow para orquestrar pipelines de machine learning:

```python
from prefect import flow, task
import mlflow
from mlflow.tracking import MlflowClient

@task
def treinar_modelo(data_path, params):
    """Treina um modelo ML e registra no MLflow"""
    mlflow.set_experiment("modelo_previsao")
    
    with mlflow.start_run() as run:
        # Registrar parâmetros
        mlflow.log_params(params)
        
        # Treinar modelo (exemplo simplificado)
        modelo = train_model_function(data_path, params)
        
        # Registrar métricas
        metrics = evaluate_model(modelo)
        mlflow.log_metrics(metrics)
        
        # Salvar modelo
        mlflow.sklearn.log_model(modelo, "model")
        
        return run.info.run_id, metrics

@task
def registrar_modelo(run_id, metrics, min_accuracy=0.75):
    """Registra o modelo no Model Registry se atender aos critérios"""
    if metrics["accuracy"] >= min_accuracy:
        client = MlflowClient()
        model_uri = f"runs:/{run_id}/model"
        model_details = mlflow.register_model(model_uri, "modelo_producao")
        return {"status": "registered", "version": model_details.version}
    else:
        return {"status": "rejected", "accuracy": metrics["accuracy"]}

@flow(name="ML Training Pipeline")
def ml_training_pipeline(data_path, params):
    """Flow de treinamento e registro de modelo ML"""
    run_id, metrics = treinar_modelo(data_path, params)
    registro = registrar_modelo(run_id, metrics)
    return registro
```

## Paralelismo e Concorrência

O Prefect suporta execução paralela e distribuída de fluxos de trabalho:

```python
from prefect import flow, task
import time
from prefect.task_runners import ConcurrentTaskRunner

@task
def processar_batch(batch_id):
    """Processa um lote de dados"""
    time.sleep(2)  # Simulando processamento
    return f"Batch {batch_id} processado"

@flow(name="Processamento Paralelo", task_runner=ConcurrentTaskRunner())
def processamento_paralelo():
    """Flow com execução paralela de tasks"""
    # Submete 10 tasks para execução paralela
    resultados = []
    for i in range(10):
        resultado = processar_batch.submit(i)
        resultados.append(resultado)
    
    # Espera todos os resultados
    return [r.result() for r in resultados]
```

## Armazenamento de Configurações com Block Storage

O Prefect 2.0 introduziu o conceito de Blocks para armazenamento de configurações:

```python
from prefect.blocks.system import Secret
from prefect_aws import S3Bucket

# Registrar um segredo
secret_block = Secret.load("minio-credentials")
access_key = secret_block.get()

# Configurar acesso ao S3/MinIO
s3_block = S3Bucket(
    bucket_path="silver",
    credentials={
        "access_key": access_key,
        "secret_key": secret_block.get(),
    }
)
s3_block.save("minio-silver")

# Usar em um flow
@flow
def acessar_dados():
    bucket = S3Bucket.load("minio-silver")
    data = bucket.read_path("data/vendas.csv")
    return data
```

## Boas Práticas

- **Idempotência**: Projete seus flows para serem idempotentes, executando múltiplas vezes com o mesmo resultado
- **Tratamento de Falhas**: Use `retry` e `timeout` para gerenciar falhas nas tasks
- **Parâmetros**: Utilize parâmetros para tornar seus flows reutilizáveis
- **Notificações**: Configure notificações para falhas em flows críticos
- **Monitoramento**: Utilize a interface web para monitorar o estado dos flows
- **Armazenamento de Estado**: Configure armazenamento persistente para estado dos flows
- **Versionamento**: Mantenha flows versionados em controle de código
- **Documentação**: Documente flows com docstrings e anotações

## Log e Monitoramento Avançado

```python
from prefect import flow, task
from prefect import get_run_logger

@task
def processar_dados(data):
    logger = get_run_logger()
    logger.info(f"Iniciando processamento de {len(data)} registros")
    
    # Processamento
    result = transform_data(data)
    
    logger.info(f"Processamento concluído: {len(result)} registros processados")
    return result

@flow(log_prints=True)
def pipeline_processo():
    print("Iniciando pipeline de processamento")
    dados = carregar_dados()
    resultado = processar_dados(dados)
    print(f"Pipeline concluído com {len(resultado)} resultados")
```

## Solução de Problemas

- **Falha na Conexão**: Verifique se todos os serviços estão em execução (`docker-compose ps`)
- **Erro em Tasks**: Inspecione os logs detalhados na interface web do Prefect
- **Problemas com Spark**: Verifique se as configurações do Spark estão corretas para seu ambiente
- **Tasks Bloqueadas**: Verifique por deadlocks ou recursos insuficientes
- **Falhas de Implantação**: Confirme que o worker está corretamente configurado e conectado

## Recursos Adicionais

- [Documentação Oficial do Prefect](https://docs.prefect.io/)
- [Prefect API Reference](https://docs.prefect.io/api-ref/)
- [Repositório GitHub do Prefect](https://github.com/PrefectHQ/prefect)
- [Comunidade Prefect no Slack](https://prefect.io/slack)
- [Prefect Cloud](https://app.prefect.cloud/) (para ambientes de produção)
