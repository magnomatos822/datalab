# JupyterHub no DataFlow Lab

## Visão Geral

[JupyterHub](https://jupyter.org/hub) é uma plataforma multi-usuário para notebooks Jupyter, permitindo que equipes de analistas e cientistas de dados colaborem em um ambiente centralizado. No DataFlow Lab, o JupyterHub serve como o principal ambiente de desenvolvimento para análise exploratória, visualização de dados e prototipagem de modelos de machine learning.

## Recursos Principais

- **Notebooks Multi-usuário**: Ambiente compartilhado para toda a equipe
- **Autenticação**: Sistema integrado de autenticação e autorização
- **Persistência**: Armazenamento persistente dos notebooks e arquivos
- **Extensibilidade**: Suporte para extensões e pacotes personalizados
- **Integração com Spark**: Conectividade nativa com clusters Spark

## Como Utilizar

### Acessando o JupyterHub

1. Após iniciar o ambiente com `docker-compose up -d`, acesse:
   - URL: http://localhost:8888
   - Credenciais:
     - Usuário padrão: `admin`
     - Senha padrão: `admin`  
     *(Nota: Altere as credenciais em ambientes de produção)*

### Principais Funcionalidades

#### Criando um Novo Notebook

1. Na interface inicial, clique em "New" e selecione "Python 3"
2. O novo notebook será criado com um kernel Python padrão
3. Digite código em células e execute com Shift+Enter ou o botão "Run"

#### Conectando-se ao Spark

Para realizar análises distribuídas com Spark:

```python
from pyspark.sql import SparkSession

# Configuração com suporte ao Delta Lake
spark = (SparkSession.builder
         .appName("DataFlow-Lab-Analysis")
         .config("spark.jars.packages", "io.delta:delta-core_2.12:2.3.0")
         .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
         .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
         .getOrCreate())

# Acessando dados da camada silver
df = spark.read.format("delta").load("s3a://silver/customers")

# Visualização inicial dos dados
df.show(5)
```

#### Acessando Dados no MinIO/S3

Para acessar dados armazenados no MinIO:

```python
import pandas as pd
import boto3
from io import BytesIO

# Configurar cliente S3 apontando para MinIO
s3_client = boto3.client(
    's3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    region_name='us-east-1'
)

# Listar buckets disponíveis
response = s3_client.list_buckets()
for bucket in response['Buckets']:
    print(f"Bucket: {bucket['Name']}")

# Ler um arquivo CSV diretamente do MinIO
obj = s3_client.get_object(Bucket='bronze', Key='sample/data.csv')
df = pd.read_csv(BytesIO(obj['Body'].read()))
```

#### Visualização de Dados

Exemplo de como criar visualizações:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração visual
plt.style.use('ggplot')
plt.figure(figsize=(12, 8))

# Gráfico de barras simples
sns.barplot(x='categoria', y='vendas', data=df)
plt.title('Vendas por Categoria')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Gráfico de série temporal
df_ts = df.groupby('data')['vendas'].sum().reset_index()
plt.figure(figsize=(14, 6))
plt.plot(df_ts['data'], df_ts['vendas'], marker='o')
plt.title('Vendas ao Longo do Tempo')
plt.grid(True, alpha=0.3)
plt.show()
```

#### Integração com MLflow

Para rastrear experimentos de machine learning:

```python
import mlflow
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Configurar MLflow - conectando ao servidor do MLflow no Docker
mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("Previsão de Vendas")

# Preparar dados
X = df[['feature1', 'feature2', 'feature3']]
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Iniciar experimento MLflow
with mlflow.start_run():
    # Definir parâmetros
    params = {
        'n_estimators': 100,
        'max_depth': 5,
        'random_state': 42
    }
    
    # Treinar modelo
    model = RandomForestRegressor(**params)
    model.fit(X_train, y_train)
    
    # Avaliar modelo
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2 = r2_score(y_test, y_pred)
    
    # Registrar parâmetros e métricas
    mlflow.log_params(params)
    mlflow.log_metric("RMSE", rmse)
    mlflow.log_metric("R2", r2)
    
    # Registrar o modelo
    mlflow.sklearn.log_model(model, "random_forest_model")
    
    print(f"RMSE: {rmse:.4f}")
    print(f"R2: {r2:.4f}")
    print(f"Modelo registrado no MLflow")
```

## Estrutura de Diretórios

O JupyterHub no DataFlow Lab mantém seus arquivos na seguinte estrutura:

```
/home/jovyan/
├── notebooks/            # Notebooks principais
├── data/                 # Arquivos de dados locais
├── scripts/              # Scripts Python auxiliares
└── reports/              # Notebooks para relatórios
```

## Extensões Recomendadas

O ambiente já inclui várias extensões úteis:

- **jupyterlab-git**: Integração com git para versionamento
- **jupyterlab-toc**: Tabela de conteúdo automática para notebooks
- **jupyterlab-sql**: Consultas SQL direto do notebook
- **jupyterlab-plotly**: Integração com gráficos Plotly

## Boas Práticas

- **Notebooks Modulares**: Divida análises complexas em múltiplos notebooks
- **Documentação**: Use células markdown para documentar seu raciocínio
- **Código Reutilizável**: Mova funções reutilizáveis para módulos Python
- **Checkpoints**: Salve regularmente e crie versões dos notebooks importantes
- **Limpeza de Recursos**: Encerre conexões Spark quando não estiverem sendo usadas

## Solução de Problemas

- **Kernel morrendo**: Verifique o uso de memória, pode ser necessário aumentar os limites
- **Conexão com MinIO/Spark**: Verifique se as URLs e credenciais estão corretas
- **Pacotes ausentes**: Use `!pip install` para instalar pacotes adicionais
- **Notebooks lentos**: Considere otimizar o código ou utilizar amostragem para conjuntos grandes

## Recursos Adicionais

- [Documentação Oficial do JupyterHub](https://jupyterhub.readthedocs.io/)
- [Documentação do JupyterLab](https://jupyterlab.readthedocs.io/)
- [Guias de Melhores Práticas para Notebooks](https://jupyterbook.org/en/stable/)
