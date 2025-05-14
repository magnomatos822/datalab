# MLflow - Gerenciamento do Ciclo de Vida de Machine Learning

![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)

> Versão: 2.22.0

## O que é MLflow?

MLflow é uma plataforma de código aberto para gerenciar o ciclo de vida completo de machine learning. Ele permite rastrear experimentos, empacotar código em formatos reproduzíveis e compartilhar e implantar modelos.

## Componentes Principais

O MLflow oferece os seguintes componentes principais:

1. **MLflow Tracking**: Acompanhamento de experimentos para registrar e comparar parâmetros e resultados
2. **MLflow Projects**: Empacotamento de código ML em formato reproduzível
3. **MLflow Models**: Convenção para empacotamento de modelos em diversos formatos de ML
4. **MLflow Registry**: Armazenamento centralizado para gerenciar o ciclo de vida completo do modelo

## Como Acessar

O MLflow está disponível em:

- **URL**: http://localhost:5000
- **Tracking URI**: `http://mlflow:5000` (dentro dos contêineres)
- **Default Artifact Location**: `s3://mlflow/`

## Integração com o DataLab

No DataFlow Lab, o MLflow está configurado para:

1. Usar o MinIO como armazenamento de artefatos (compatível com S3)
2. Utilizar SQLite como backend store (adequado para desenvolvimento)
3. Integrar-se com o ambiente Spark para modelos de ML escaláveis

## Estrutura de Armazenamento

```
data/mlflow/
└── db/
    └── mlflow.db     # Banco de dados SQLite para metadados

mlruns/                # Experimentos e artefatos locais
└── models/            # Diretório para modelos registrados
```

## Uso Básico

### Rastrear um Experimento

```python
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

# Definir o servidor de rastreamento
mlflow.set_tracking_uri("http://localhost:5000")

# Iniciar um experimento
mlflow.set_experiment("exemplo-regressao")

# Carregar e preparar dados
data = pd.read_csv("s3://bronze/raw_data_source1/table1/dados.csv")
X = data.drop("target", axis=1)
y = data["target"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Iniciar execução de MLflow
with mlflow.start_run():
    # Definir parâmetros
    params = {
        "n_estimators": 100,
        "max_depth": 6,
        "min_samples_split": 5
    }
    mlflow.log_params(params)
    
    # Treinar modelo
    rf = RandomForestRegressor(**params)
    rf.fit(X_train, y_train)
    
    # Registrar métricas
    preds = rf.predict(X_test)
    rmse = ((preds - y_test) ** 2).mean() ** 0.5
    r2 = rf.score(X_test, y_test)
    
    mlflow.log_metrics({
        "rmse": rmse,
        "r2": r2
    })
    
    # Salvar modelo
    mlflow.sklearn.log_model(rf, "modelo-rf", registered_model_name="RandomForestRegressor")
    
    # Salvar artefato adicional
    mlflow.log_artifact("path/to/diagram.png", "diagramas")
    
    print(f"Modelo salvo com RMSE: {rmse:.4f}, R²: {r2:.4f}")
```

## Registrando Modelos

O Model Registry do MLflow permite versionar e gerenciar o ciclo de vida dos modelos:

```python
from mlflow.tracking import MlflowClient

# Criar um cliente do MLflow
client = MlflowClient()

# Obter o modelo mais recente
latest_model = client.get_latest_versions("RandomForestRegressor", stages=["None"])[0]

# Promover o modelo para produção
client.transition_model_version_stage(
    name="RandomForestRegressor",
    version=latest_model.version,
    stage="Production"
)

# Documentar o modelo
client.update_model_version(
    name="RandomForestRegressor",
    version=latest_model.version,
    description="Modelo de previsão de vendas treinado em 14/05/2025"
)
```

## Servindo Modelos

Para servir um modelo registrado:

```python
import mlflow.pyfunc

# Carregar o modelo
model_name = "RandomForestRegressor"
model_version = 1
model = mlflow.pyfunc.load_model(f"models:/{model_name}/{model_version}")

# Fazer predições
predictions = model.predict(X_test)
```

## Integração com PySpark

Exemplo de uso com PySpark:

```python
import mlflow
import mlflow.spark
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator

# Definir o URI do MLflow
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("spark-experiment")

# Preparar dados
train_df = spark.read.format("delta").load("s3://silver/clean_data_domain1/table1")
test_df = spark.read.format("delta").load("s3://silver/clean_data_domain1/table1_test")

# Treinar modelo
rf = RandomForestRegressor(featuresCol="features", labelCol="target")

with mlflow.start_run() as run:
    # Treinar modelo
    model = rf.fit(train_df)
    
    # Avaliar modelo
    predictions = model.transform(test_df)
    evaluator = RegressionEvaluator(labelCol="target", predictionCol="prediction", metricName="rmse")
    rmse = evaluator.evaluate(predictions)
    
    # Log parâmetros e métricas
    mlflow.log_params({"numTrees": rf.getNumTrees, "maxDepth": rf.getMaxDepth})
    mlflow.log_metric("rmse", rmse)
    
    # Log do modelo Spark
    mlflow.spark.log_model(model, "spark_model", registered_model_name="SparkRandomForest")
```

## Variáveis de Ambiente

O MLflow no DataLab está configurado com as seguintes variáveis:

| Variável                | Valor                   | Descrição                              |
|-------------------------|-------------------------|----------------------------------------|
| MLFLOW_S3_ENDPOINT_URL  | http://minio:9000       | Endpoint MinIO para artefatos         |
| AWS_ACCESS_KEY_ID       | ${AWS_ACCESS_KEY_ID}    | Credencial de acesso ao MinIO         |
| AWS_SECRET_ACCESS_KEY   | ${AWS_SECRET_ACCESS_KEY}| Chave secreta de acesso ao MinIO      |

## Melhores Práticas

1. **Organizar experimentos**: Use experimentos diferentes para diferentes casos de uso ou equipes
2. **Registrar todos os parâmetros**: Documente todos os hiperparâmetros relevantes
3. **Salvar artefatos complementares**: Gráficos, explicações, matrizes de confusão, etc.
4. **Versionar dados**: Use referências para versões específicas de datasets
5. **Anotar runs importantes**: Adicione descrições e tags para identificar experimentos bem-sucedidos
6. **Definir estágios**: Use o registro de modelos para controlar o ciclo de vida (Staging, Production, Archived)

## Limitações e Soluções

- **Performance do SQLite**: Para produção com múltiplos usuários, considere migrar para PostgreSQL
- **Latência do MinIO**: Para cargas maiores, configure buckets dedicados
- **Gerenciamento de dependências**: Use MLflow Projects ou Docker para garantir reprodutibilidade

## Recursos Adicionais

- [Documentação Oficial do MLflow](https://www.mlflow.org/docs/latest/index.html)
- [Exemplos Práticos](https://github.com/mlflow/mlflow/tree/master/examples)
- [MLflow com Delta Lake](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/index.html)

## Resolução de Problemas

| Problema | Solução |
|----------|--------|
| O MLflow não está acessível | Verifique se o contêiner está rodando: `docker-compose ps mlflow` |
| Erro de autenticação no MinIO | Verifique as credenciais AWS no arquivo `.env` |
| Erros de permissão | O MLflow roda como root, verifique permissões dos volumes |
| Modelo muito grande | Configure variável `MLFLOW_ARTIFACT_UPLOAD_DOWNLOAD_CHUNK_SIZE` |
