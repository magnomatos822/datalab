# DataFlow Lab

<div align="center">
  <img src="https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white" alt="Apache Spark">
  <img src="https://img.shields.io/badge/Delta_Lake-00ADD8?style=for-the-badge&logo=delta&logoColor=white" alt="Delta Lake">
  <img src="https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white" alt="MLflow">
  <img src="https://img.shields.io/badge/MinIO-C72E49?style=for-the-badge&logo=minio&logoColor=white" alt="MinIO">
  <img src="https://img.shields.io/badge/Prefect-2EBDFA?style=for-the-badge&logo=prefect&logoColor=white" alt="Prefect">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="JupyterHub">
  <img src="https://img.shields.io/badge/Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white" alt="Apache Kafka">
  <img src="https://img.shields.io/static/v1?style=for-the-badge&message=Apache+NiFi&color=728E9B&logo=Apache+NiFi&logoColor=FFFFFF&label=" alt="Apache NiFi">
</div>

> Última atualização: 14 de maio de 2025

## 🔍 Visão Geral

DataFlow Lab é um ambiente completo de desenvolvimento para engenharia de dados, ciência de dados e MLOps que integra as melhores ferramentas open source em uma única plataforma. O projeto implementa a arquitetura Medallion (Bronze, Silver, Gold) oferecendo um ambiente completo para processamento de dados em larga escala.

## ✨ Características Principais

- **Arquitetura Medallion**: Implementação completa das camadas Bronze, Silver e Gold
- **Processamento Distribuído**: Apache Spark para processamento em larga escala
- **Armazenamento Resiliente**: Delta Lake para gerenciamento de dados confiável
- **Machine Learning**: MLflow para tracking, registro e deployment de modelos
- **Orquestração**: Prefect para orquestração de fluxos de dados
- **Ingestão de Dados**: Apache NiFi para automatizar a ingestão de várias fontes
- **Streaming**: Apache Kafka para processamento de streaming em tempo real
- **Visualização**: Streamlit para dashboards e aplicações de dados interativas
- **Ambiente de Desenvolvimento**: JupyterHub para colaboração e experimentação

## 📋 Componentes

| Componente       | Versão                       | Porta       | Descrição                              | Documentação                               |
| ---------------- | ---------------------------- | ----------- | -------------------------------------- | ------------------------------------------ |
| **Apache Spark** | 3.5.1                        | 8080, 7077  | Processamento distribuído de dados     | [Documentação](/docs/spark/README.md)      |
| **Delta Lake**   | 3.3.1                        | -           | Camada de armazenamento para lakehouse | [Documentação](/docs/spark/README.md)      |
| **MLflow**       | 2.22.0                       | 5000        | Plataforma de MLOps                    | [Documentação](/docs/mlflow/README.md)     |
| **MinIO**        | RELEASE.2025-04-22T22-12-26Z | 9000, 9001  | Armazenamento de objetos S3            | [Documentação](/docs/minio/README.md)      |
| **Prefect**      | 3.4.1                        | 4200        | Orquestração de fluxos                 | [Documentação](/docs/prefect/README.md)    |
| **Streamlit**    | 1.45.0                       | 8501        | Dashboards interativos                 | [Documentação](/docs/streamlit/README.md)  |
| **JupyterHub**   | 4.0.2                        | 8000        | Ambiente de desenvolvimento            | [Documentação](/docs/jupyterhub/README.md) |
| **Apache Kafka** | 7.5.0                        | 9092, 29092 | Streaming de eventos                   | [Documentação](/docs/kafka/README.md)      |
| **Apache NiFi**  | 2.4.0                        | 8443        | Automação de fluxo de dados            | [Documentação](/docs/nifi/README.md)       |

## 🏗️ Arquitetura

A arquitetura do DataFlow Lab é baseada no padrão Medallion (Lakehouse), organizada em três camadas principais:

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CAMADA DE INGESTÃO                         │
│                                                                     │
│  ┌──────────┐    ┌───────────┐    ┌────────┐    ┌────────────────┐  │
│  │  Apache  │    │  Apache   │    │  APIs/ │    │     Outros     │  │
│  │   NiFi   │    │   Kafka   │    │  REST  │    │    Coletores   │  │
│  └────┬─────┘    └─────┬─────┘    └───┬────┘    └────────┬───────┘  │
│       │                │               │                 │          │
└───────┼────────────────┼───────────────┼─────────────────┼──────────┘
        │                │               │                 │
        ▼                ▼               ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   ┌─────────────────────────┐                       │
│                   │       BRONZE LAYER      │                       │
│                   │    (Dados Brutos em     │                       │
│                   │     Formato Delta)      │                       │
│                   └────────────┬────────────┘                       │
│                                │                                    │
│                   ┌────────────▼────────────┐                       │
│                   │       SILVER LAYER      │                       │
│                   │   (Dados Limpos com     │                       │
│                   │  Qualidade Garantida)   │                       │
│                   └────────────┬────────────┘                       │
│                                │                                    │
│                   ┌────────────▼────────────┐                       │
│                   │        GOLD LAYER       │                       │
│                   │  (Dados Agregados para  │                       │
│                   │        Consumo)         │                       │
│                   └─────────────────────────┘                       │
│                             MINIO                                   │
└─────────────────────────────────────────────────────────────────────┘
        │                │               │                 │
        ▼                ▼               ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          CAMADA DE CONSUMO                          │
│                                                                     │
│  ┌──────────┐    ┌───────────┐    ┌────────┐    ┌────────────────┐  │
│  │Streamlit │    │  MLflow   │    │ Apache │    │    Outros      │  │
│  │Dashboards│    │  Models   │    │ Spark  │    │  Consumidores  │  │
│  └──────────┘    └───────────┘    └────────┘    └────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

A arquitetura Medallion possui três camadas principais:

1. **Bronze**: Dados brutos ingeridos exatamente como foram recebidos
2. **Silver**: Dados limpos, validados e transformados
3. **Gold**: Dados agregados e preparados para consumo por aplicações

## 🚀 Como Começar

### Pré-requisitos

- Docker
- Docker Compose
- Git

### Instalação e Inicialização

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/datalab.git
   cd datalab
   ```

2. Inicie os serviços:
   ```bash
   docker-compose up -d
   ```

3. Acesse os componentes pelos seguintes URLs (após alguns minutos para inicialização):
   - JupyterHub: [http://localhost:8000](http://localhost:8000) (admin/admin)
   - MinIO Console: [http://localhost:9001](http://localhost:9001) (admin/admin123)
   - Apache Spark UI: [http://localhost:8080](http://localhost:8080)
   - MLflow UI: [http://localhost:5000](http://localhost:5000)
   - Prefect UI: [http://localhost:4200](http://localhost:4200)
   - Streamlit: [http://localhost:8501](http://localhost:8501)
   - Apache NiFi: [https://localhost:8443/nifi](https://localhost:8443/nifi) (nifi/HGd15bvfv8744ghbdhgdv7895agqERAo)
   - Kafka UI: [http://localhost:8090](http://localhost:8090)

### Inicializando os Buckets MinIO

Os buckets do MinIO são inicializados automaticamente na primeira execução. Se necessário, você pode inicializá-los manualmente:

```bash
./scripts/init_minio.sh
```

## 📚 Tutoriais e Exemplos

### JupyterHub

O JupyterHub contém vários notebooks de exemplo para ajudá-lo a começar:

1. Autentique-se em [http://localhost:8000](http://localhost:8000) com as credenciais `admin`/`admin`
2. Navegue até a pasta `examples/` para ver os notebooks de exemplo
3. Comece com o notebook `medallion_architecture.ipynb` para uma visão geral da arquitetura

### Exemplos de Arquitetura Medallion

- **Ingestão para Bronze**: Consulte o notebook `examples/bronze_ingestion.ipynb`
- **Processamento Bronze para Silver**: Consulte o notebook `examples/silver_processing.ipynb`
- **Agregações Silver para Gold**: Consulte o notebook `examples/gold_aggregations.ipynb`

## 📋 Casos de Uso Comuns

### 1. Processamento de Dados Completo

```python
# No JupyterHub, usando PySpark com Delta Lake
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Inicialização do Spark com suporte a Delta
spark = SparkSession.builder \
    .appName("MedallionExample") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "admin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .getOrCreate()

# 1. Ler da camada Bronze
bronze_df = spark.read.format("delta").load("s3a://bronze/raw_data_source1/table1")

# 2. Processar para Silver (limpeza e transformação)
silver_df = bronze_df \
    .dropDuplicates() \
    .filter(col("valor") > 0) \
    .withColumn("processed_date", current_date())

# 3. Salvar na camada Silver
silver_df.write.format("delta") \
    .mode("overwrite") \
    .save("s3a://silver/clean_data_domain1/table1")

# 4. Processar para Gold (agregação para análise)
gold_df = silver_df \
    .groupBy("categoria", "região") \
    .agg(sum("valor").alias("valor_total")) \
    .orderBy(desc("valor_total"))

# 5. Salvar na camada Gold
gold_df.write.format("delta") \
    .mode("overwrite") \
    .save("s3a://gold/analytics_domain1/dashboard1")
```

### 2. Machine Learning com MLflow

```python
# No JupyterHub
import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Configurar MLflow
mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("modelo-classificacao")

# Carregar dados da camada Silver
spark = SparkSession.builder.getOrCreate()
data = spark.read.format("delta").load("s3a://silver/clean_data_domain1/table1").toPandas()

# Preparar dados
X = data.drop("target_column", axis=1)
y = data["target_column"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Treinar com tracking do MLflow
with mlflow.start_run():
    # Configurações do modelo
    params = {"n_estimators": 100, "max_depth": 10, "random_state": 42}
    mlflow.log_params(params)
    
    # Treinar modelo
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    
    # Avaliar modelo
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    
    # Registrar métricas
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    
    # Registrar modelo
    mlflow.sklearn.log_model(model, "random_forest_model")
    
    print(f"Treinamento concluído - Acurácia: {accuracy:.4f}")
```

### 3. Orquestração com Prefect

```python
# No JupyterHub ou em um arquivo Python
from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner
from pyspark.sql import SparkSession

@task(retries=3, retry_delay_seconds=30)
def extract_bronze_data(source):
    spark = SparkSession.builder.getOrCreate()
    return spark.read.format("delta").load(f"s3a://bronze/{source}")

@task
def transform_to_silver(df):
    from pyspark.sql.functions import current_timestamp, col
    
    return df.dropDuplicates() \
        .filter(col("valor") > 0) \
        .withColumn("processed_ts", current_timestamp())

@task
def load_to_silver(df, destination):
    df.write.format("delta") \
        .mode("overwrite") \
        .save(f"s3a://silver/{destination}")
    return f"s3a://silver/{destination}"

@flow(task_runner=SequentialTaskRunner())
def bronze_to_silver_etl(source="raw_data_source1/table1", destination="clean_data_domain1/table1"):
    # Extract
    raw_data = extract_bronze_data(source)
    
    # Transform
    transformed_data = transform_to_silver(raw_data)
    
    # Load
    result_path = load_to_silver(transformed_data, destination)
    
    return result_path

# Execução
if __name__ == "__main__":
    result = bronze_to_silver_etl()
    print(f"ETL concluído! Dados armazenados em: {result}")
```

## 📈 Painéis e Visualizações

Crie visualizações interativas com Streamlit:

1. Acesse o Streamlit em [http://localhost:8501](http://localhost:8501)
2. Use os painéis pré-configurados ou crie novos com base nos dados das camadas Gold

## 🔄 Fluxos de Ingestão

Configure fluxos de ingestão de dados com Apache NiFi:

1. Acesse o NiFi em [https://localhost:8443/nifi](https://localhost:8443/nifi) (usuário: nifi, senha: HGd15bvfv8744ghbdhgdv7895agqERAo)
2. Importe os templates de fluxo disponíveis ou crie novos fluxos de ingestão

## 🎯 Casos de Uso

O DataFlow Lab é adequado para:

- **Engenharia de Dados**: Construção de pipelines ETL/ELT robustos
- **Data Science**: Experimentação, validação e deployment de modelos
- **Analytics**: Criação de painéis e relatórios interativos
- **MLOps**: Ciclo completo de vida de modelos de machine learning
- **Streaming**: Processamento de dados em tempo real
- **Governança de Dados**: Catalogação e linhagem de dados

## 💡 Funcionalidades Avançadas

### 1. Integração com Contas Cloud

Para usar com provedores de nuvem, configure suas credenciais:

```yaml
# Em docker-compose.yml, adicione as variáveis de ambiente
environment:
  - AWS_ACCESS_KEY_ID=sua-chave
  - AWS_SECRET_ACCESS_KEY=sua-senha
```

### 2. Escalabilidade

Para escalar o processamento, ajuste os recursos no docker-compose.yml:

```yaml
services:
  spark-worker:
    deploy:
      replicas: 3  # Aumentar número de workers
    environment:
      - SPARK_WORKER_CORES=4
      - SPARK_WORKER_MEMORY=8g
```

### 3. Segurança

Configure autenticação e autorização mais robustas:

```yaml
services:
  jupyterhub:
    environment:
      - JUPYTERHUB_ADMIN_USER=seunome
      - JUPYTERHUB_ADMIN_PASSWORD=senha-segura
```

## 🛠️ Manutenção e Resolução de Problemas

### Comandos Úteis

```bash
# Ver logs de um serviço
docker-compose logs -f [serviço]

# Reiniciar um serviço específico
docker-compose restart [serviço]

# Verificar uso de recursos
docker stats

# Parar todos os serviços
docker-compose down

# Remover volumes (cuidado - apaga todos os dados)
docker-compose down -v
```

### Problemas Comuns

| Problema                  | Solução                                                             |
| ------------------------- | ------------------------------------------------------------------- |
| Erro de conexão com MinIO | Verifique se o serviço está rodando e as credenciais estão corretas |
| Jupyter não carrega       | Verifique logs e se há memória suficiente disponível                |
| Erro Spark Connection     | Verifique status do serviço spark-master                            |
| Lentidão no processamento | Considere aumentar recursos dos workers                             |
| Falhas no MLflow          | Verifique conexão com o banco de dados do MLflow                    |

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie sua feature branch (`git checkout -b feature/amazing-feature`)
3. Commit suas alterações (`git commit -m 'Add amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📚 Recursos Adicionais

- [Documentação da Arquitetura Medallion](https://docs.databricks.com/lakehouse/medallion.html)
- [Guia do Delta Lake](https://docs.delta.io/latest/index.html)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [Prefect Documentação](https://docs.prefect.io/)
- [Apache Spark Guia](https://spark.apache.org/docs/latest/)
- [Streamlit Documentação](https://docs.streamlit.io/)
- [MinIO Reference](https://docs.min.io/)
- [Apache Kafka](https://kafka.apache.org/documentation/)
- [Apache NiFi Guide](https://nifi.apache.org/docs.html)
- [JupyterHub](https://jupyterhub.readthedocs.io/en/stable/)
