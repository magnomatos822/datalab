import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="DataFlow Lab - Tutorial", layout="wide")

st.title("🔄 DataFlow Lab - Tutorial")

st.markdown(
    """
Este é um tutorial básico para começar a usar o DataFlow Lab, nossa plataforma integrada de Data Lakehouse.
Vamos percorrer os principais componentes e mostrar como você pode começar a processar dados usando
a arquitetura Medallion.
"""
)

# Tabs para diferentes partes do tutorial
tab1, tab2, tab3, tab4 = st.tabs(
    ["Introdução", "Arquitetura Medallion", "Exemplos", "Próximos Passos"]
)

with tab1:
    st.header("Bem-vindo ao DataFlow Lab!")

    st.markdown(
        """
    ## O que é o DataFlow Lab?
    
    O DataFlow Lab é uma plataforma completa de Data Lakehouse que integra as melhores ferramentas 
    open-source para processamento de dados e machine learning:
    
    - **Apache Spark**: Processamento distribuído
    - **Delta Lake**: Garantias ACID para seu data lake
    - **MinIO**: Armazenamento compatível com S3
    - **MLflow**: Gerenciamento do ciclo de vida de ML
    - **Prefect**: Orquestração de fluxos de dados
    - **Airbyte**: Integração de dados
    - **JupyterHub**: Ambiente de desenvolvimento
    - **Streamlit**: Visualização de dados
    """
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Principais benefícios")
        st.markdown(
            """
        - Confiabilidade e consistência com Delta Lake
        - Escalabilidade com Spark
        - Reprodutibilidade de experimentos
        - Orquestração de ponta a ponta
        - Implementação rápida
        """
        )

    with col2:
        st.subheader("URLs dos Serviços")
        services = {
            "MinIO Console": "http://localhost:9001",
            "Spark Master": "http://localhost:8080",
            "MLflow": "http://localhost:5000",
            "Prefect": "http://localhost:4200",
            "JupyterHub": "http://localhost:8888",
            "Airbyte": "http://localhost:8000",
        }

        for service, url in services.items():
            st.markdown(f"- **{service}**: [{url}]({url})")

with tab2:
    st.header("Arquitetura Medallion")

    st.markdown(
        """
    A arquitetura Medallion (também conhecida como multi-hop) organiza o processamento
    de dados em camadas, melhorando a qualidade e confiabilidade dos dados conforme progridem
    pelas camadas.
    """
    )

    # Criar dados para visualização da arquitetura
    layers = ["Raw Data", "Bronze Layer", "Silver Layer", "Gold Layer", "ML Models"]
    quality = [10, 30, 60, 90, 95]
    trust = [5, 40, 70, 95, 98]
    structure = [0, 20, 75, 95, 95]

    data = pd.DataFrame(
        {
            "Layer": layers,
            "Data Quality": quality,
            "Trust Level": trust,
            "Data Structure": structure,
        }
    )

    # Gráfico da arquitetura
    fig = px.line(
        data,
        x="Layer",
        y=["Data Quality", "Trust Level", "Data Structure"],
        title="Progressão da Qualidade de Dados na Arquitetura Medallion",
        markers=True,
        line_shape="spline",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Explicação de cada camada
    st.subheader("Bronze Layer")
    st.markdown(
        """
    A camada Bronze armazena dados brutos, exatamente como foram ingeridos das fontes de origem.
    
    **Características**:
    - Preservação dos dados originais
    - Mínima ou nenhuma transformação
    - Metadados de ingestão (timestamp, fonte)
    - Retenção para auditoria
    """
    )

    st.subheader("Silver Layer")
    st.markdown(
        """
    A camada Silver armazena dados limpos, validados e transformados.
    
    **Características**:
    - Dados estruturados e tipados
    - Validação de esquema
    - Tratamento de valores nulos
    - Remoção de duplicatas
    - Normalize/padronização
    """
    )

    st.subheader("Gold Layer")
    st.markdown(
        """
    A camada Gold armazena dados refinados e agregados para consumo por analistas e cientistas de dados.
    
    **Características**:
    - Dados agregados e modelados
    - Feature engineering
    - Tabelas e views para BI
    - Otimizados para consulta
    - Disponíveis para dashboards
    """
    )

with tab3:
    st.header("Exemplos Práticos")

    st.subheader("Exemplo 1: Processamento de Dados na Arquitetura Medallion")

    with st.expander("Ver código do exemplo"):
        st.code(
            """
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, lit

# Criar sessão Spark com suporte ao Delta Lake e MinIO
spark = SparkSession.builder \\
    .appName("MedallionExample") \\
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \\
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \\
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \\
    .config("spark.hadoop.fs.s3a.access.key", "admin") \\
    .config("spark.hadoop.fs.s3a.secret.key", "admin123") \\
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \\
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \\
    .getOrCreate()

# 1. CAMADA BRONZE - Ingestão de dados brutos
df = spark.read.format("csv") \\
    .option("header", "true") \\
    .load("/data/raw_data.csv")
    
# Adicionar metadados
bronze_df = df \\
    .withColumn("ingestion_time", current_timestamp()) \\
    .withColumn("source", lit("csv_file"))

# Salvar na camada Bronze
bronze_df.write \\
    .format("delta") \\
    .mode("overwrite") \\
    .save("s3a://bronze/dataset")

# 2. CAMADA SILVER - Limpeza e transformação
silver_df = spark.read.format("delta") \\
    .load("s3a://bronze/dataset")
    
# Limpeza de dados
silver_df = silver_df \\
    .dropDuplicates() \\
    .na.fill(0, ["numeric_column"]) \\
    .na.fill("unknown", ["string_column"]) \\
    .filter(col("id").isNotNull())

# Salvar na camada Silver
silver_df.write \\
    .format("delta") \\
    .mode("overwrite") \\
    .save("s3a://silver/dataset")

# 3. CAMADA GOLD - Agregação e modelagem
gold_df = spark.read.format("delta") \\
    .load("s3a://silver/dataset")

# Agregações
summary_df = gold_df \\
    .groupBy("category") \\
    .agg(
        avg("value").alias("avg_value"),
        sum("quantity").alias("total_quantity"),
        count("*").alias("count")
    )

# Salvar na camada Gold
summary_df.write \\
    .format("delta") \\
    .mode("overwrite") \\
    .save("s3a://gold/dataset_summary")
        """
        )

    st.subheader("Exemplo 2: Integração com MLflow")

    with st.expander("Ver código do exemplo"):
        st.code(
            """
import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Configurar MLflow
mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("housing_price_prediction")

# Carregar dados da camada Gold
df = spark.read.format("delta").load("s3a://gold/housing_features").toPandas()

# Preparar dados
X = df.drop("price", axis=1)
y = df["price"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treinar modelo com rastreamento MLflow
with mlflow.start_run():
    # Parâmetros do modelo
    n_estimators = 100
    max_depth = 10
    
    # Registrar parâmetros
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    
    # Treinar modelo
    model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth)
    model.fit(X_train, y_train)
    
    # Avaliar modelo
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2 = r2_score(y_test, y_pred)
    
    # Registrar métricas
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)
    
    # Salvar modelo
    mlflow.sklearn.log_model(model, "random_forest_model")
    
    # Registrar modelo no Registry
    model_uri = f"runs:/{mlflow.active_run().info.run_id}/random_forest_model"
    mlflow.register_model(model_uri, "housing_price_predictor")
        """
        )

    st.subheader("Exemplo 3: Orquestração com Prefect")

    with st.expander("Ver código do exemplo"):
        st.code(
            """
from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner
from pyspark.sql import SparkSession

@task(name="Ingerir Dados")
def ingest_bronze_data():
    # Configurar Spark
    spark = SparkSession.builder.appName("PrefectFlow").getOrCreate()
    
    # Ingerir dados
    df = spark.read.format("csv") \\
        .option("header", "true") \\
        .load("/data/raw_data.csv")
        
    # Salvar na camada bronze
    df.write.format("delta") \\
        .mode("overwrite") \\
        .save("s3a://bronze/dataset")
        
    return "s3a://bronze/dataset"

@task(name="Transformar Dados")
def transform_to_silver(bronze_path):
    # Configurar Spark
    spark = SparkSession.builder.appName("PrefectFlow").getOrCreate()
    
    # Ler dados da camada bronze
    df = spark.read.format("delta").load(bronze_path)
    
    # Transformar dados
    clean_df = df.dropDuplicates()
    
    # Salvar na camada silver
    clean_df.write.format("delta") \\
        .mode("overwrite") \\
        .save("s3a://silver/dataset")
        
    return "s3a://silver/dataset"

@task(name="Agregar Dados")
def aggregate_to_gold(silver_path):
    # Configurar Spark
    spark = SparkSession.builder.appName("PrefectFlow").getOrCreate()
    
    # Ler dados da camada silver
    df = spark.read.format("delta").load(silver_path)
    
    # Agregar dados
    agg_df = df.groupBy("category").agg(...)
    
    # Salvar na camada gold
    agg_df.write.format("delta") \\
        .mode("overwrite") \\
        .save("s3a://gold/dataset_agg")
        
    return "s3a://gold/dataset_agg"

@flow(name="ETL Pipeline", 
      description="Pipeline ETL completo da arquitetura Medallion",
      task_runner=SequentialTaskRunner())
def medallion_pipeline():
    # Executa as tarefas em sequência
    bronze_path = ingest_bronze_data()
    silver_path = transform_to_silver(bronze_path)
    gold_path = aggregate_to_gold(silver_path)
    
    return {
        "bronze_path": bronze_path,
        "silver_path": silver_path,
        "gold_path": gold_path
    }

if __name__ == "__main__":
    medallion_pipeline()
        """
        )

    # Demonstração interativa
    st.subheader("Demonstração Interativa: Criando uma Tabela Delta")

    st.markdown(
        """
    Esta demonstração simula a criação de uma tabela Delta Lake na arquitetura Medallion.
    Escolha os parâmetros e veja a transformação dos dados entre as camadas.
    """
    )

    # Parâmetros de entrada
    col1, col2 = st.columns(2)
    with col1:
        rows = st.slider("Número de Registros", 10, 100, 20)
        noise = st.slider("Nível de Ruído (%)", 0, 50, 10)

    with col2:
        missing = st.slider("Dados Ausentes (%)", 0, 50, 5)
        outliers = st.slider("Outliers (%)", 0, 20, 2)

    # Gerar dados simulados
    def generate_data(rows, noise, missing, outliers):
        np.random.seed(42)

        # Dados base
        x = np.linspace(0, 10, rows)
        y = 2 * x + 1 + noise / 10 * np.random.randn(rows)

        # Adicionar outliers
        outlier_count = int(rows * outliers / 100)
        outlier_idx = np.random.choice(range(rows), outlier_count, replace=False)
        y[outlier_idx] = y[outlier_idx] * 5

        # Adicionar valores ausentes
        missing_count = int(rows * missing / 100)
        missing_idx = np.random.choice(range(rows), missing_count, replace=False)

        # Criar DataFrame
        df = pd.DataFrame(
            {
                "id": range(1, rows + 1),
                "x": x,
                "y": y,
                "category": np.random.choice(["A", "B", "C"], size=rows),
            }
        )

        # Aplicar valores ausentes
        df.loc[missing_idx, "y"] = None

        return df

    # Gerar dados para as diferentes camadas
    bronze_df = generate_data(rows, noise, missing, outliers)

    # Camada Silver (limpeza)
    silver_df = bronze_df.copy()
    silver_df = silver_df.dropna()  # Remover valores ausentes

    # Detectar e remover outliers com IQR
    Q1 = silver_df["y"].quantile(0.25)
    Q3 = silver_df["y"].quantile(0.75)
    IQR = Q3 - Q1
    silver_df = silver_df[
        (silver_df["y"] >= Q1 - 1.5 * IQR) & (silver_df["y"] <= Q3 + 1.5 * IQR)
    ]

    # Camada Gold (agregação)
    gold_df = (
        silver_df.groupby("category")
        .agg(
            count=("id", "count"),
            mean_y=("y", "mean"),
            min_y=("y", "min"),
            max_y=("y", "max"),
        )
        .reset_index()
    )

    # Visualizar os dados
    st.subheader("Visualização das Camadas de Dados")

    tabs = st.tabs(["Bronze", "Silver", "Gold"])

    with tabs[0]:
        st.write("**Dados Brutos (Bronze)**")
        st.dataframe(bronze_df)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(
            bronze_df["x"],
            bronze_df["y"],
            c=bronze_df["category"].map({"A": "red", "B": "green", "C": "blue"}),
        )
        ax.set_title("Dados Bronze - Com Ruído, Valores Ausentes e Outliers")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        st.pyplot(fig)

    with tabs[1]:
        st.write("**Dados Limpos (Silver)**")
        st.dataframe(silver_df)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(
            silver_df["x"],
            silver_df["y"],
            c=silver_df["category"].map({"A": "red", "B": "green", "C": "blue"}),
        )
        ax.set_title("Dados Silver - Limpos e Normalizados")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        st.pyplot(fig)

    with tabs[2]:
        st.write("**Dados Agregados (Gold)**")
        st.dataframe(gold_df)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(
            gold_df["category"],
            gold_df["mean_y"],
            yerr=gold_df["max_y"] - gold_df["mean_y"],
        )
        ax.set_title("Dados Gold - Agregados por Categoria")
        ax.set_xlabel("Categoria")
        ax.set_ylabel("Média de Y")
        st.pyplot(fig)

with tab4:
    st.header("Próximos Passos")

    st.markdown(
        """
    ## Aprofunde seus conhecimentos
    
    Agora que você já conhece os conceitos básicos do DataFlow Lab, aqui estão alguns
    próximos passos para continuar sua jornada:
    
    1. **Explore os Notebooks de Exemplo**:
       - `/notebooks/magnomatos822/amazon.ipynb`: Análise de dados financeiros da Amazon
       - `/notebooks/tutorials/`: Tutoriais detalhados para cada componente
    
    2. **Crie seu próprio Pipeline Medallion**:
       - Use a classe `MedallionArchitecture` em `app/medallion_architecture.py`
       - Orquestre com Prefect usando o `app/medallion_prefect_flow.py`
    
    3. **Integre Fontes de Dados com Airbyte**:
       - Configure conectores para suas fontes de dados
       - Direcione para a camada Bronze
    
    4. **Desenvolva Modelos de ML**:
       - Use dados da camada Gold para features
       - Rastreie experimentos com MLflow
       - Implemente modelos em produção
    
    5. **Crie Dashboards com Streamlit**:
       - Visualize dados da camada Gold
       - Compartilhe insights com sua equipe
    """
    )

    st.info(
        """
    **Precisa de Ajuda?**
    
    Consulte a documentação detalhada em `/docs/` para cada componente.
    """
    )

    # Mostrar gráfico de avanço de habilidades
    st.subheader("Curva de Aprendizado")

    skills = ["Básico", "Bronze", "Silver", "Gold", "Expert"]
    time = [1, 3, 7, 14, 30]
    knowledge = [10, 30, 60, 85, 95]

    fig = px.line(
        x=skills,
        y=knowledge,
        markers=True,
        labels={"x": "Nível", "y": "Conhecimento (%)"},
        title="Progresso de Aprendizado do DataFlow Lab",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Call to action
    st.success(
        "Estamos ansiosos para ver o que você vai construir com o DataFlow Lab! 🚀"
    )
