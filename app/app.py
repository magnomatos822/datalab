"""
Aplicação Streamlit para visualização e interação com o DataFlow Lab
"""

import json
import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from PIL import Image

# Configuração da página
st.set_page_config(page_title="DataFlow Lab Dashboard", page_icon="📊", layout="wide")

# Título e descrição
st.title("🔄 DataFlow Lab - Dashboard")
st.markdown(
    """
    Painel de controle para monitoramento e interação com a plataforma DataFlow Lab.
    Este dashboard permite visualizar dados, monitorar pipelines e interagir com os serviços.
"""
)

# Sidebar com navegação
st.sidebar.title("Navegação")
page = st.sidebar.radio(
    "Selecione uma página",
    ["Visão Geral", "Camadas", "Pipelines", "Serviços", "ML Models"],
)


# Status dos serviços
@st.cache_data(ttl=60)  # Cache por 60 segundos
def check_service_status(url):
    try:
        response = requests.get(url, timeout=1)
        if response.status_code < 400:
            return "🟢 Online"
        else:
            return "🟠 Problema"
    except:
        return "🔴 Offline"


# Funções para simular dados
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_sample_data():
    # Dados simulados para demonstração
    dates = pd.date_range(end=datetime.now(), periods=30).tolist()
    bronze_counts = [100 + i * 10 + int(i**1.5) for i in range(30)]
    silver_counts = [bronze_counts[i] * 0.8 for i in range(30)]
    gold_counts = [silver_counts[i] * 0.6 for i in range(30)]

    df = pd.DataFrame(
        {
            "date": dates,
            "bronze": bronze_counts,
            "silver": silver_counts,
            "gold": gold_counts,
        }
    )

    return df


@st.cache_data
def get_pipeline_data():
    # Dados simulados para demonstração de pipelines
    now = datetime.now()
    pipelines = [
        {
            "name": "ETL_Financial",
            "last_run": (now - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Sucesso",
            "duration": "5m 12s",
            "records": 15420,
        },
        {
            "name": "Stock_Data_Ingestion",
            "last_run": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Sucesso",
            "duration": "3m 45s",
            "records": 8750,
        },
        {
            "name": "Customer_Analytics",
            "last_run": (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Falha",
            "duration": "2m 30s",
            "records": 0,
        },
        {
            "name": "Product_Metrics",
            "last_run": (now - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Sucesso",
            "duration": "8m 20s",
            "records": 25300,
        },
        {
            "name": "ML_Training_Daily",
            "last_run": (now - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Sucesso",
            "duration": "15m 45s",
            "records": 42680,
        },
    ]
    return pd.DataFrame(pipelines)


@st.cache_data
def get_model_data():
    # Dados simulados sobre modelos de ML
    models = [
        {
            "name": "price_prediction_v1",
            "type": "RandomForest",
            "accuracy": 0.87,
            "created": "2025-05-08",
            "status": "Production",
        },
        {
            "name": "customer_churn_v2",
            "type": "XGBoost",
            "accuracy": 0.92,
            "created": "2025-05-09",
            "status": "Staging",
        },
        {
            "name": "product_recommendation",
            "type": "Neural Network",
            "accuracy": 0.78,
            "created": "2025-05-10",
            "status": "Development",
        },
        {
            "name": "anomaly_detector_v1",
            "type": "Isolation Forest",
            "accuracy": 0.81,
            "created": "2025-05-07",
            "status": "Production",
        },
    ]
    return pd.DataFrame(models)


# Página principal - Visão Geral
if page == "Visão Geral":
    st.header("Visão Geral do DataFlow Lab")

    # Status dos serviços em cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("**MinIO**")
        st.write(check_service_status("http://minio:9000"))
    with col2:
        st.info("**Spark**")
        st.write(check_service_status("http://spark-master:8080"))
    with col3:
        st.info("**MLflow**")
        st.write(check_service_status("http://mlflow:5000"))
    with col4:
        st.info("**Prefect**")
        st.write(check_service_status("http://prefect:4200"))

    # Gráfico de dados
    st.subheader("Volume de Dados por Camada")
    df = get_sample_data()

    chart = px.line(
        df,
        x="date",
        y=["bronze", "silver", "gold"],
        title="Evolução do Volume de Dados",
        labels={"value": "Registros", "date": "Data", "variable": "Camada"},
        color_discrete_map={
            "bronze": "#cd7f32",
            "silver": "#c0c0c0",
            "gold": "#ffd700",
        },
    )
    st.plotly_chart(chart, use_container_width=True)

    # Últimos pipelines executados
    st.subheader("Últimos Pipelines Executados")
    pipelines_df = get_pipeline_data()

    # Colorir o status
    def color_status(val):
        color = "green" if val == "Sucesso" else "red"
        return f"background-color: {color}; color: white"

    styled_df = pipelines_df.style.applymap(color_status, subset=["status"])

    st.dataframe(styled_df, use_container_width=True)

# Página de camadas
elif page == "Camadas":
    st.header("Arquitetura Medallion")

    layer_tabs = st.tabs(["Bronze", "Silver", "Gold"])

    with layer_tabs[0]:
        st.subheader("Camada Bronze")
        st.markdown(
            """
        A camada Bronze contém dados brutos ingeridos sem modificações ou com modificações mínimas.
        Principais características:
        - Preserva os dados originais para auditoria e recuperação
        - Inclui metadados como hora de ingestão e fonte
        - Armazenada em formato Delta Lake para garantias ACID
        """
        )

        st.info("**Tabelas na camada Bronze**")
        bronze_tables = [
            "raw_financial_data",
            "raw_stock_data",
            "raw_customer_data",
            "raw_logs",
        ]
        for table in bronze_tables:
            st.code(f"s3a://bronze/{table}")

    with layer_tabs[1]:
        st.subheader("Camada Silver")
        st.markdown(
            """
        A camada Silver contém dados limpos, validados e transformados.
        Principais características:
        - Dados normalizados e estruturados
        - Valores nulos tratados e anomalias removidas
        - Esquema consistente e documentado
        """
        )

        st.info("**Tabelas na camada Silver**")
        silver_tables = [
            "clean_financial_data",
            "clean_stock_data",
            "clean_customer_data",
        ]
        for table in silver_tables:
            st.code(f"s3a://silver/{table}")

    with layer_tabs[2]:
        st.subheader("Camada Gold")
        st.markdown(
            """
        A camada Gold contém dados refinados e agregados para consumo.
        Principais características:
        - Tabelas e views preparadas para análise
        - Dados agregados e modelados para casos de uso específicos
        - Otimizados para consulta e análise
        """
        )

        st.info("**Tabelas na camada Gold**")
        gold_tables = [
            "financial_metrics",
            "stock_analysis",
            "customer_segments",
            "dashboards",
        ]
        for table in gold_tables:
            st.code(f"s3a://gold/{table}")

# Página de Pipelines
elif page == "Pipelines":
    st.header("Pipelines de Dados")
    st.markdown(
        """
    Aqui você pode monitorar e gerenciar os pipelines de dados da plataforma.
    Os pipelines são orquestrados com Prefect e processam dados através das camadas.
    """
    )

    # Formulário para criar um novo pipeline
    with st.expander("Criar Novo Pipeline"):
        with st.form("new_pipeline_form"):
            st.subheader("Novo Pipeline")
            name = st.text_input("Nome do Pipeline")
            source_type = st.selectbox(
                "Tipo de Fonte",
                ["PostgreSQL", "MySQL", "API", "CSV", "Parquet", "JSON"],
            )
            target_table = st.text_input("Tabela de Destino")
            schedule = st.selectbox(
                "Agendamento", ["Diário", "Horário", "Semanal", "Mensal", "Manual"]
            )

            # Adicionar botão para enviar
            submitted = st.form_submit_button("Criar Pipeline")
            if submitted:
                st.success(f"Pipeline '{name}' criado com sucesso!")

    # Lista de pipelines
    st.subheader("Pipelines Ativos")
    pipelines_df = get_pipeline_data()

    # Filtros
    status_filter = st.selectbox("Filtrar por Status", ["Todos", "Sucesso", "Falha"])
    if status_filter != "Todos":
        pipelines_df = pipelines_df[pipelines_df["status"] == status_filter]

    # Mostrar tabela
    st.dataframe(pipelines_df, use_container_width=True)

    # Detalhes do pipeline
    st.subheader("Detalhes do Pipeline")
    selected_pipeline = st.selectbox(
        "Selecione um pipeline para ver detalhes", pipelines_df["name"].tolist()
    )

    # Botões de ação
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Executar Agora"):
            st.info(f"Executando pipeline {selected_pipeline}...")
            st.success(f"Pipeline {selected_pipeline} iniciado com sucesso!")
    with col2:
        st.button("Editar Pipeline")
    with col3:
        st.button("Pausar Pipeline")

    # Mostrar logs simulados
    st.subheader("Logs do Pipeline")
    st.code(
        f"""
    [2025-05-11 08:30:15] INFO: Pipeline {selected_pipeline} iniciado
    [2025-05-11 08:30:18] INFO: Conectando à fonte de dados
    [2025-05-11 08:30:25] INFO: Dados extraídos com sucesso (12345 registros)
    [2025-05-11 08:31:05] INFO: Dados transformados
    [2025-05-11 08:32:10] INFO: Dados carregados na camada destino
    [2025-05-11 08:32:15] INFO: Pipeline concluído com sucesso
    """
    )

# Página de Serviços
elif page == "Serviços":
    st.header("Serviços da Plataforma")
    st.markdown(
        """
    Aqui você pode monitorar e acessar os diversos serviços que compõem a plataforma DataFlow Lab.
    """
    )

    # Cartões para os serviços com links
    col1, col2 = st.columns(2)

    with col1:
        st.info("### MinIO")
        st.write("Sistema de armazenamento de objetos compatível com S3")
        st.write("- Console: [http://localhost:9001](http://localhost:9001)")
        st.write("- Status: ", check_service_status("http://minio:9000"))
        if st.button("Inicializar Buckets"):
            st.success("Buckets bronze, silver e gold criados com sucesso!")

    with col2:
        st.info("### Apache Spark")
        st.write("Framework de processamento distribuído")
        st.write("- UI: [http://localhost:8080](http://localhost:8080)")
        st.write("- Status: ", check_service_status("http://spark-master:8080"))
        if st.button("Ver Aplicações Ativas"):
            st.code(
                """
            ApplicationID: spark-20250511123456-0001
            Nome: medallion_example
            Estado: RUNNING
            Cores: 2
            Memória: 2.0 GB
            """
            )

    col3, col4 = st.columns(2)

    with col3:
        st.info("### MLflow")
        st.write("Plataforma para gerenciamento do ciclo de vida de ML")
        st.write("- UI: [http://localhost:5000](http://localhost:5000)")
        st.write("- Status: ", check_service_status("http://mlflow:5000"))
        if st.button("Ver Experimentos"):
            st.dataframe(
                {
                    "ID": [1, 2, 3],
                    "Nome": ["price_prediction", "customer_churn", "anomaly_detection"],
                    "Execuções": [15, 8, 23],
                }
            )

    with col4:
        st.info("### Prefect")
        st.write("Orquestrador de fluxos de dados")
        st.write("- UI: [http://localhost:4200](http://localhost:4200)")
        st.write("- Status: ", check_service_status("http://prefect:4200"))
        if st.button("Ver Fluxos"):
            st.dataframe(
                {
                    "Nome": ["medallion_pipeline", "etl_diário", "treinamento_ml"],
                    "Estado": ["Healthy", "Healthy", "Warning"],
                    "Última Execução": [
                        "11/05/2025 08:30",
                        "11/05/2025 04:00",
                        "10/05/2025 22:00",
                    ],
                }
            )

# Página de ML Models
elif page == "ML Models":
    st.header("Machine Learning Models")
    st.markdown(
        """
    Aqui você pode monitorar e gerenciar os modelos de Machine Learning da plataforma.
    Os modelos são treinados com dados da camada Gold e rastreados com MLflow.
    """
    )

    # Lista de modelos
    models_df = get_model_data()

    # Filtros
    model_status = st.selectbox(
        "Filtrar por Status", ["Todos", "Production", "Staging", "Development"]
    )
    if model_status != "Todos":
        models_df = models_df[models_df["status"] == model_status]

    # Mostrar tabela
    st.dataframe(models_df, use_container_width=True)

    # Gráfico de barras para acurácia
    fig = px.bar(
        models_df,
        x="name",
        y="accuracy",
        color="type",
        title="Acurácia dos Modelos",
        labels={"name": "Nome do Modelo", "accuracy": "Acurácia", "type": "Tipo"},
    )
    st.plotly_chart(fig, use_container_width=True)

    # Formulário para treinar novo modelo
    with st.expander("Treinar Novo Modelo"):
        with st.form("train_model_form"):
            st.subheader("Novo Modelo")
            name = st.text_input("Nome do Modelo")
            model_type = st.selectbox(
                "Tipo de Modelo",
                [
                    "RandomForest",
                    "XGBoost",
                    "Neural Network",
                    "Linear Regression",
                    "Isolation Forest",
                ],
            )
            dataset = st.selectbox(
                "Dataset de Treinamento",
                [
                    "gold.financial_metrics",
                    "gold.customer_segments",
                    "gold.stock_analysis",
                ],
            )
            target = st.text_input("Variável Alvo")

            # Adicionar botão para enviar
            submitted = st.form_submit_button("Treinar Modelo")
            if submitted:
                st.success(f"Treinamento do modelo '{name}' iniciado!")

    # Botão para implementar modelo em produção
    selected_model = st.selectbox(
        "Selecione um modelo para ação", models_df["name"].tolist()
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Promover para Produção"):
            st.success(f"Modelo {selected_model} promovido para produção!")
    with col2:
        st.button("Ver Métricas Detalhadas")
    with col3:
        st.button("Baixar Modelo")

# Rodapé
st.markdown("---")
st.markdown("DataFlow Lab Dashboard | Atualizado em: 11 de maio de 2025")
