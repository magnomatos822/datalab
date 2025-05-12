# Prefect no DataFlow Lab

## Visão Geral

[Prefect](https://www.prefect.io/) é uma plataforma moderna de orquestração de fluxos de trabalho para dados. No DataFlow Lab, o Prefect é utilizado para orquestrar, programar e monitorar os fluxos de transformação de dados entre as camadas Bronze, Silver e Gold do nosso Data Lakehouse.

## Componentes Principais

- **Flows**: Unidades fundamentais de trabalho no Prefect, representam sua lógica de negócios
- **Tasks**: Unidades atômicas dentro de um flow, realizando operações específicas
- **Schedules**: Programação de execução de flows em intervalos definidos
- **UI Web**: Interface para visualizar, monitorar e gerenciar execuções
- **API**: Permite integração com outras ferramentas e sistemas

## Como Utilizar

### Acessando a Interface Web do Prefect

1. Após iniciar o ambiente com `docker-compose up -d`, acesse:
   - URL: http://localhost:4200
   - Não há autenticação por padrão na instalação local

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

## Boas Práticas

- **Idempotência**: Projete seus flows para serem idempotentes, executando múltiplas vezes com o mesmo resultado
- **Tratamento de Falhas**: Use `retry` e `timeout` para gerenciar falhas nas tasks
- **Parâmetros**: Utilize parâmetros para tornar seus flows reutilizáveis
- **Notificações**: Configure notificações para falhas em flows críticos
- **Monitoramento**: Utilize a interface web para monitorar o estado dos flows

## Solução de Problemas

- **Falha na Conexão**: Verifique se todos os serviços estão em execução (`docker-compose ps`)
- **Erro em Tasks**: Inspecione os logs detalhados na interface web do Prefect
- **Problemas com Spark**: Verifique se as configurações do Spark estão corretas para seu ambiente

## Recursos Adicionais

- [Documentação Oficial do Prefect](https://docs.prefect.io/)
- [Prefect API Reference](https://docs.prefect.io/api-ref/)
