# MLflow no DataFlow Lab

## Visão Geral

MLflow é uma plataforma de código aberto para gerenciar o ciclo de vida completo de machine learning. No DataFlow Lab, o MLflow é utilizado para rastrear experimentos, gerenciar modelos e facilitar a implementação de modelos de machine learning.

## Componentes do MLflow

O MLflow no DataFlow Lab inclui os seguintes componentes principais:

1. **MLflow Tracking**: Registra e consulta experimentos, incluindo parâmetros, métricas, código e artefatos
2. **MLflow Projects**: Empacota código em formato reproduzível
3. **MLflow Models**: Gerencia e implanta modelos em diversos ambientes
4. **MLflow Registry**: Gerencia o ciclo de vida completo do modelo

## Acessando o MLflow

- **UI**: [http://localhost:5000](http://localhost:5000)
- **API Python**: Disponível através da biblioteca `mlflow`

## Configuração no DataFlow Lab

O MLflow está configurado para armazenar:

- **Metadados**: Em um banco de dados SQLite local
- **Artefatos**: No MinIO (bucket `mlflow`)

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

## Troubleshooting

Problemas comuns e soluções:

1. **Erro de conexão**: Verifique se o servidor MLflow está em execução
2. **Erro ao salvar artefatos**: Verifique as credenciais do MinIO
3. **Modelos não aparecem no Registry**: Verifique se o registro foi bem-sucedido

## Referências

- [Documentação Oficial do MLflow](https://mlflow.org/docs/latest/index.html)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [MLflow Models](https://mlflow.org/docs/latest/models.html)
- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
