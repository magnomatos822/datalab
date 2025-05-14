# JupyterHub - Ambiente de Desenvolvimento Colaborativo

<div align="center">
  <img src="https://img.shields.io/badge/JupyterHub-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="JupyterHub">
</div>

> Versão: 4.0.2

## O que é JupyterHub?

JupyterHub é uma plataforma multi-usuário que permite hospedar notebooks Jupyter para múltiplos usuários com autenticação, permissões e recursos personalizados. No DataFlow Lab, o JupyterHub serve como o ambiente central de desenvolvimento para cientistas de dados e engenheiros, fornecendo acesso a todos os componentes do ecossistema de dados através de uma interface familiar baseada em notebooks.

## Características Principais

- **Multi-usuário**: Suporte a múltiplos usuários com isolamento de ambientes
- **Autenticação Configurável**: Suporte a diferentes métodos de autenticação
- **Kernels Diversos**: Python, PySpark, R, e outros
- **Escalabilidade**: Pode escalar de um único servidor a um cluster Kubernetes
- **Compartilhamento**: Colaboração facilitada entre equipes
- **Integração**: Conexão direta com o ecossistema de big data

## Como Acessar

O JupyterHub está disponível em:

- **URL**: [http://localhost:8000](http://localhost:8000)
- **Credenciais Padrão**:
  - Usuário: admin
  - Senha: admin

## Ambientes e Kernels Disponíveis

O JupyterHub no DataFlow Lab vem pré-configurado com os seguintes kernels:

1. **Python 3**: Ambiente Python padrão com bibliotecas de ciência de dados
2. **PySpark**: Kernel com integração ao cluster Apache Spark
3. **R**: Ambiente R para análises estatísticas (opcional)

## Bibliotecas Pré-instaladas

### Python/PySpark

```
pandas==2.0.2
numpy==1.24.4
matplotlib==3.8.2
seaborn==0.13.0
scikit-learn==1.3.2
delta-spark==3.3.1
pyspark==3.5.5
pyarrow==19.0.1
mlflow==2.22.0
prefect==3.4.1
boto3==1.34.7
plotly==5.22.0
streamlit==1.45.0
jupyterlab==4.0.11
jupyter-server-proxy==4.2.0
ipywidgets==8.1.1
```

### R (Opcional)

```
tidyverse
sparklyr
ggplot2
rmarkdown
shiny
```

## Estrutura de Diretórios

Cada usuário no JupyterHub tem seu próprio espaço de trabalho isolado:

```
/home/jovyan/
├── work/                    # Diretório padrão mapeado para trabalho do usuário
│   └── [arquivos do usuário]
├── shared/                  # Pasta compartilhada entre usuários
│   ├── datasets/            # Conjuntos de dados compartilhados
│   └── notebooks/           # Notebooks compartilhados
└── examples/                # Notebooks de exemplo e tutoriais
    ├── spark/               # Exemplos de uso do Spark
    ├── mlflow/              # Exemplos de integração com MLflow
    └── medallion/           # Exemplos da arquitetura Medallion
```

## Conexão com outros Componentes

### 1. Integração com Apache Spark

O kernel PySpark está pré-configurado para se conectar ao cluster Spark:

```python
# Isso já está configurado no kernel PySpark, mas pode ser usado no Python normal também
from pyspark.sql import SparkSession

# Criar sessão Spark com suporte a Delta Lake
spark = SparkSession.builder \
    .appName("JupyterNotebook") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "admin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Exemplo de leitura de dados
df = spark.read.format("delta").load("s3a://silver/clean_data_domain1/table1")
df.show(5)
```

### 2. Integração com MLflow

Acesso direto ao servidor MLflow para rastreamento de experimentos:

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np

# Configurar MLflow
mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("jupyter_experiment")

# Treinar modelo com tracking
with mlflow.start_run():
    # Dados de exemplo
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3
    
    # Parâmetros do modelo
    params = {"n_estimators": 100, "max_depth": 4}
    mlflow.log_params(params)
    
    # Treinar modelo
    model = RandomForestRegressor(**params)
    model.fit(X, y)
    
    # Log métricas
    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)
    mlflow.log_metric("mse", mse)
    
    # Log modelo
    mlflow.sklearn.log_model(model, "random_forest_model")
    
    print(f"MSE: {mse}")
    print(f"Run ID: {mlflow.active_run().info.run_id}")
```

### 3. Acesso ao MinIO (S3)

Acesso direto aos dados armazenados no MinIO:

```python
import boto3
from botocore.client import Config

# Configurar cliente S3
s3_client = boto3.client(
    's3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='admin',
    aws_secret_access_key='admin123',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

# Listar buckets
response = s3_client.list_buckets()
for bucket in response['Buckets']:
    print(f"Bucket: {bucket['Name']}")

# Listar objetos em um bucket
response = s3_client.list_objects_v2(
    Bucket='bronze',
    Prefix='raw_data_source1/'
)

for obj in response.get('Contents', []):
    print(f"Objeto: {obj['Key']}")
```

### 4. Orquestração com Prefect

Criar e executar fluxos Prefect diretamente dos notebooks:

```python
from prefect import flow, task
import pandas as pd

@task
def extract():
    # Extrair dados
    return pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

@task
def transform(data):
    # Transformar dados
    data['C'] = data['A'] + data['B']
    return data

@task
def load(data):
    # Carregar dados
    print("Dados processados:")
    print(data)
    return "Sucesso"

@flow
def etl_flow():
    data = extract()
    transformed = transform(data)
    result = load(transformed)
    return result

# Executar o fluxo
if __name__ == "__main__":
    result = etl_flow()
    print(f"Resultado: {result}")
```

### 5. Desenvolvimento de Dashboards com Streamlit

Criar e testar aplicações Streamlit:

```python
%%writefile app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Dados de exemplo
data = pd.DataFrame({
    'x': range(1, 11),
    'y': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
})

# Interface Streamlit
st.title('Meu Dashboard Streamlit')
st.write('Um exemplo simples de dashboard')

# Gráfico
fig, ax = plt.subplots()
ax.plot(data['x'], data['y'])
st.pyplot(fig)

# Tabela de dados
st.write('Dados:')
st.dataframe(data)
```

E depois execute com:

```bash
!streamlit run app.py
```

## Trabalhando com a Arquitetura Medallion

### Exemplo de Fluxo Completo no JupyterHub

```python
# Importações
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, col
import os

# Criar sessão Spark
spark = SparkSession.builder \
    .appName("MedallionArchitecture") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "admin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .getOrCreate()

# 1. Camada Bronze - Ingestão de dados brutos
# Simulando ingestão de CSV
bronze_data = spark.read.csv("s3a://bronze/raw_data_source1/table1/sales_data.csv", header=True, inferSchema=True)

# Adicionar metadados de ingestão
bronze_data = bronze_data.withColumn("ingestion_time", current_timestamp())

# Visualizar dados
print("Dados na camada Bronze:")
bronze_data.show(5)

# Salvar na camada Bronze (opcional, já que assumimos que os dados já foram ingeridos)
bronze_data.write.format("delta").mode("overwrite").save("s3a://bronze/raw_data_source1/table1")

# 2. Camada Silver - Limpeza e transformação
silver_data = bronze_data.dropDuplicates() \
    .filter(col("valor") > 0) \
    .withColumn("processed_time", current_timestamp())

# Visualizar dados limpos
print("\nDados na camada Silver:")
silver_data.show(5)

# Salvar na camada Silver
silver_data.write.format("delta").mode("overwrite").save("s3a://silver/clean_data_domain1/table1")

# 3. Camada Gold - Agregações e modelagem para consumo
gold_data = silver_data.groupBy("categoria", "regiao") \
    .agg({"valor": "sum"}) \
    .withColumnRenamed("sum(valor)", "valor_total") \
    .orderBy("valor_total", ascending=False)

# Visualizar dados agregados
print("\nDados na camada Gold:")
gold_data.show(5)

# Salvar na camada Gold
gold_data.write.format("delta").mode("overwrite").save("s3a://gold/analytics_domain1/sales_by_category")

# 4. Visualização de métricas
print("\nMétricas principais:")
print(f"Total de registros na camada Bronze: {bronze_data.count()}")
print(f"Total de registros na camada Silver: {silver_data.count()}")
print(f"Total de registros na camada Gold: {gold_data.count()}")
print(f"Valor total de vendas: {gold_data.agg({'valor_total': 'sum'}).collect()[0][0]}")
```

## Gerenciamento de Usuários

### Adicionar Novos Usuários

A adição de novos usuários pode ser feita através da interface de administração ou via linha de comando:

```bash
# Acessar o container
docker exec -it jupyterhub bash

# Criar um novo usuário
useradd -m -s /bin/bash novousuario
echo "novousuario:senha" | chpasswd

# Adicionar ao grupo de usuários do Jupyter
usermod -a -G jupyterhub novousuario
```

### Configuração de Cotas e Recursos

O JupyterHub está configurado para limitar os recursos por usuário:

- **CPU**: 2 cores por usuário
- **RAM**: 4GB por usuário
- **Armazenamento**: 10GB por usuário

## Extensões Úteis

O ambiente JupyterLab vem com várias extensões pré-instaladas:

1. **Jupyterlab Git**: Interface Git integrada
2. **Jupyterlab Debugger**: Ferramenta de depuração
3. **Table of Contents**: Navegação facilitada em notebooks longos
4. **Variable Inspector**: Inspecionar variáveis durante o desenvolvimento
5. **Jupyterlab-LSP**: Language Server Protocol para autocompletar e linting

## Boas Práticas 

### 1. Organização de Notebooks

- Use uma estrutura de diretórios consistente
- Nomeie notebooks de forma descritiva e com versão
- Adicione documentação no início do notebook

### 2. Otimização de Recursos

- Libere recursos não utilizados (desconectar kernels inativos)
- Feche conexões Spark quando não estiverem em uso
- Use `%%capture` para capturar saídas muito grandes

### 3. Versionamento

- Utilize o Git para controle de versão
- Considere usar jupytext para versionamento de notebooks como scripts

### 4. Reprodutibilidade

- Documente dependências e versões
- Use ambientes virtuais para isolamento
- Defina seeds para processos aleatórios

## Resolução de Problemas

| Problema                | Solução                                           |
| ----------------------- | ------------------------------------------------- |
| Kernel travando         | Verifique o uso de memória, reinicie o kernel     |
| Conexão Spark falha     | Verifique se o cluster Spark está ativo           |
| Notebook não salva      | Verifique permissões de arquivo e espaço em disco |
| Pacotes Python faltando | Use `!pip install pacote` no notebook             |
| JupyterHub inacessível  | Verifique logs: `docker logs jupyterhub`          |

## Exemplos e Tutoriais

O diretório `/home/jovyan/examples` contém vários notebooks de exemplo:

1. **spark_basics.ipynb**: Introdução ao Apache Spark
2. **delta_lake_demo.ipynb**: Trabalhando com tabelas Delta Lake
3. **mlflow_tracking.ipynb**: Rastreamento de experimentos com MLflow
4. **medallion_architecture.ipynb**: Implementação da arquitetura Medallion
5. **streaming_example.ipynb**: Processamento de streaming com Spark

## Recursos Adicionais

- [Documentação Oficial do JupyterHub](https://jupyterhub.readthedocs.io/)
- [JupyterLab Documentação](https://jupyterlab.readthedocs.io/)
- [Guia de Configuração do JupyterHub](https://jupyterhub-tutorial.readthedocs.io/)
- [Jupyter e Big Data](https://blog.jupyter.org/jupyter-and-the-future-of-data-science-bb6740e20303)
- [Best Practices para Notebooks](https://towardsdatascience.com/jupyter-notebook-best-practices-f430a6ba8c69)
