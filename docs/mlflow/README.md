# MLflow no DataFlow Lab

## Visão Geral

MLflow é uma plataforma de código aberto para gerenciar o ciclo de vida completo de machine learning. No DataFlow Lab, o MLflow é utilizado para rastrear experimentos, gerenciar modelos e facilitar a implementação de modelos de machine learning.

Última atualização: **13 de maio de 2025**

## Componentes do MLflow

O MLflow no DataFlow Lab inclui os seguintes componentes principais:

1. **MLflow Tracking**: Registra e consulta experimentos, incluindo parâmetros, métricas, código e artefatos
2. **MLflow Projects**: Empacota código em formato reproduzível
3. **MLflow Models**: Gerencia e implanta modelos em diversos ambientes
4. **MLflow Registry**: Gerencia o ciclo de vida completo do modelo
5. **MLflow Pipelines**: Implementa fluxos de trabalho padronizados para ML (novo)

## Acessando o MLflow

- **UI**: [http://localhost:5000](http://localhost:5000)
- **API Python**: Disponível através da biblioteca `mlflow`
- **API REST**: Disponível em [http://localhost:5000/api](http://localhost:5000/api)
- **Autenticação**: O MLflow está configurado sem autenticação para ambiente de desenvolvimento local. Em ambientes de produção, recomenda-se configurar autenticação.

## Configuração no DataFlow Lab

O MLflow está configurado para armazenar:

- **Metadados**: Em um banco de dados SQLite local (`/data/mlflow/mlflow.db`)
- **Artefatos**: No MinIO (bucket `mlflow`) usando as credenciais AWS configuradas nas variáveis de ambiente:
  - AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
  - AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}

## Registrando Experimentos com MLflow

### Exemplo Básico

```python
import mlflow

# Iniciar experimento
mlflow.set_experiment("meu_experimento")

# Iniciar execução
with mlflow.start_run():
    # Parâmetros do modelo
    mlflow.log_param("alpha", 0.5)
    mlflow.log_param("l1_ratio", 0.1)
    
    # Métrica do modelo
    mlflow.log_metric("rmse", 0.876)
    mlflow.log_metric("r2", 0.923)
    
    # Artefato (como o modelo)
    mlflow.sklearn.log_model(model, "modelo")
```

### Monitorando Hiperparâmetros

```python
from sklearn.model_selection import GridSearchCV
import mlflow.sklearn

# Definir grade de parâmetros
param_grid = {
    'alpha': [0.1, 0.5, 1.0],
    'l1_ratio': [0.1, 0.5, 0.9]
}

# Configurar grid search
grid_search = GridSearchCV(model, param_grid, cv=5, scoring='neg_mean_squared_error')

# Executar com rastreamento MLflow
with mlflow.start_run(run_name="grid_search"):
    grid_search.fit(X_train, y_train)
    
    # Registrar melhor modelo
    mlflow.log_params(grid_search.best_params_)
    mlflow.log_metric("best_score", grid_search.best_score_)
    mlflow.sklearn.log_model(grid_search.best_estimator_, "best_model")
```

### Usando com PySpark

```python
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator
import mlflow.spark

# Treinar modelo
rf = RandomForestRegressor(labelCol="label", featuresCol="features")
model = rf.fit(train_data)

# Avaliar modelo
predictions = model.transform(test_data)
rmse = RegressionEvaluator(labelCol="label").evaluate(predictions)

# Registrar modelo com MLflow
with mlflow.start_run():
    mlflow.log_param("numTrees", rf.getNumTrees())
    mlflow.log_param("maxDepth", rf.getMaxDepth())
    mlflow.log_metric("rmse", rmse)
    mlflow.spark.log_model(model, "spark_model")
```

## Model Registry

O Model Registry do MLflow permite gerenciar o ciclo de vida completo de um modelo.

### Registrando um Modelo

```python
# Após treinar e rastrear o modelo com uma execução
run_id = mlflow.last_active_run().info.run_id
model_uri = f"runs:/{run_id}/model"
model_details = mlflow.register_model(model_uri, "previsao_precos")
```

### Transições de Estágio

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Promover modelo para staging
client.transition_model_version_stage(
    name="previsao_precos",
    version=1,
    stage="Staging"
)

# Promover modelo para produção
client.transition_model_version_stage(
    name="previsao_precos",
    version=1,
    stage="Production"
)
```

### Carregando um Modelo do Registry

```python
# Carregar modelo específico por versão
model = mlflow.pyfunc.load_model(model_uri="models:/previsao_precos/1")

# Carregar modelo de stage específico
model = mlflow.pyfunc.load_model(model_uri="models:/previsao_precos/Production")
```

## Integrando com Prefect

O MLflow pode ser integrado com o Prefect para rastreamento de experimentos como parte de pipelines de dados:

```python
from prefect import flow, task
import mlflow

@task
def treinar_modelo(params):
    with mlflow.start_run() as run:
        # Registrar parâmetros
        mlflow.log_params(params)
        
        # Treinar modelo
        model = treinar(params)
        
        # Registrar métricas
        metrics = avaliar(model)
        mlflow.log_metrics(metrics)
        
        # Registrar modelo
        mlflow.sklearn.log_model(model, "model")
        
        return run.info.run_id, metrics

@flow
def pipeline_treinamento(params):
    run_id, metrics = treinar_modelo(params)
    
    # Registrar modelo se performance for boa
    if metrics["accuracy"] > 0.8:
        model_uri = f"runs:/{run_id}/model"
        mlflow.register_model(model_uri, "modelo_producao")
        
    return metrics
```

## MLflow Pipelines (Novo)

MLflow Pipelines é um novo recurso que fornece estruturas padronizadas para fluxos de trabalho comuns de ML:

```python
from mlflow.pipelines import Pipeline

# Definir pipeline de classificação
pipeline = Pipeline(
    pipeline_name="classificacao_clientes",
    target_col="churn",
    primary_metric="f1_score"
)

# Executar etapas do pipeline
pipeline.run("ingest")
pipeline.run("split")
pipeline.run("transform")
pipeline.run("train")
pipeline.run("evaluate")
pipeline.run("register")
```

## Monitoramento de Modelos

Para monitorar modelos em produção, o MLflow pode ser configurado com:

```python
import mlflow.pyfunc
import pandas as pd

# Carregar modelo em produção
modelo = mlflow.pyfunc.load_model("models:/modelo_producao/Production")

# Monitorar entrada e saída
def predict_with_monitoring(data):
    # Registrar métricas de entrada
    mlflow.log_metric("input_volume", len(data))
    
    # Fazer previsão
    predictions = modelo.predict(data)
    
    # Registrar estatísticas da saída
    mlflow.log_metric("prediction_mean", predictions.mean())
    mlflow.log_metric("prediction_std", predictions.std())
    
    return predictions
```

## Comparando Experimentos

O MLflow permite comparar visualmente diferentes experimentos:

1. Acesse a UI do MLflow em [http://localhost:5000](http://localhost:5000)
2. Selecione o experimento desejado
3. Marque as execuções que deseja comparar
4. Clique em "Compare" para visualizar diferenças de parâmetros e métricas

## Boas Práticas

1. **Nomeie experimentos adequadamente**: Use nomes descritivos para experimentos
2. **Registre todos os parâmetros**: Para garantir reprodutibilidade
3. **Registre métricas de validação**: Não apenas métricas de treino
4. **Salve artefatos importantes**: Como visualizações, matrizes de confusão, etc.
5. **Use tags**: Para organizar experimentos
6. **Documente modelos**: Adicione descrições aos modelos registrados
7. **Controle de versão**: Mantenha o código-fonte versionado junto com os experimentos
8. **Automação**: Integre o MLflow em pipelines automatizados com Prefect

## Integração com Delta Lake

O MLflow se integra perfeitamente com Delta Lake:

```python
# Treinar com dados do Delta Lake
training_data = spark.read.format("delta").load("s3a://silver/training_data")

# Treinar modelo e registrar
with mlflow.start_run():
    # Treinar modelo
    model = train_model(training_data)
    
    # Registrar localização dos dados de treinamento
    mlflow.log_param("training_data_path", "s3a://silver/training_data")
    mlflow.log_param("training_data_version", delta_table.history(1).select("version").collect()[0][0])
    
    # Registrar modelo
    mlflow.sklearn.log_model(model, "model")
```

## Troubleshooting

Problemas comuns e soluções:

1. **Erro de conexão**: Verifique se o servidor MLflow está em execução
   ```bash
   docker ps | grep mlflow
   ```

2. **Erro ao salvar artefatos**: Verifique as credenciais do MinIO
   ```bash
   docker-compose logs mlflow
   ```

3. **Modelos não aparecem no Registry**: Verifique se o registro foi bem-sucedido
   ```python
   client = MlflowClient()
   client.list_registered_models()
   ```

4. **Problemas com o SQLite**: Se o banco de dados estiver corrompido, restaure de um backup
   ```bash
   cp /data/mlflow/mlflow.db.bak /data/mlflow/mlflow.db
   ```

## Referências

- [Documentação Oficial do MLflow](https://mlflow.org/docs/latest/index.html)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [MLflow Models](https://mlflow.org/docs/latest/models.html)
- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
- [MLflow Pipelines](https://mlflow.org/docs/latest/pipelines.html)
- [MLflow com Delta Lake](https://docs.databricks.com/delta/delta-intro.html)
