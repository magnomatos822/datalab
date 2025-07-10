"""
Aplicação Streamlit para visualização e interação com o DataFlow Lab
Integrada com a plataforma unificada DataLab
"""

import json
import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from PIL import Image

# Configuração da página (deve ser a primeira chamada Streamlit)
st.set_page_config(page_title="DataLab Unified Dashboard", page_icon="🚀", layout="wide")

# Importar módulos da plataforma unificada
import sys

sys.path.append("/opt/datalab")
sys.path.append(".")

try:
    from core.platform import DataLabCore
    from core.config import DataLabConfig
    from core.orchestrator import UnifiedOrchestrator
    from config.platform_config import get_platform_config, get_service_config
except ImportError:
    st.warning("Módulos da plataforma unificada não encontrados. Executando em modo fallback.")
    DataLabCore = None
    DataLabConfig = None
    UnifiedOrchestrator = None
    get_platform_config = lambda x, y: y
    get_service_config = lambda x: None


# Inicializar plataforma unificada
@st.cache_resource
def init_platform():
    """Inicializa a plataforma unificada com cache"""
    if DataLabCore and DataLabConfig and UnifiedOrchestrator:
        try:
            platform = DataLabCore()
            config_manager = DataLabConfig()
            orchestrator = UnifiedOrchestrator()
            st.success("✅ Plataforma unificada inicializada com sucesso!")
            return platform, config_manager, orchestrator
        except Exception as e:
            st.warning(f"⚠️ Não foi possível inicializar plataforma unificada: {e}")
            return None, None, None
    return None, None, None


platform, config_manager, orchestrator = init_platform()

# Título e descrição
st.title("� DataLab - Plataforma Unificada")
st.markdown(
    """
    Painel de controle unificado para monitoramento e interação com a plataforma DataLab.
    Este dashboard integra todos os serviços e permite gestão centralizada de pipelines, 
    dados e monitoramento em tempo real.
"""
)

# Status da Plataforma Unificada
if platform:
    st.info("🌟 **Plataforma Unificada Ativa** - Todos os recursos avançados habilitados")
    
    # Mostrar métricas da plataforma
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        metrics = platform.get_unified_metrics()
        platform_status = platform.get_platform_status()
        with col1:
            st.metric("Serviços Configurados", len(platform_status.get('services', {})))
        with col2:
            st.metric("Pipelines Monitorados", len(platform.get_pipelines_status()))
        with col3:
            st.metric("Health Score", f"{metrics.get('overall_health', 95)}%")
        with col4:
            st.metric("Uptime", metrics.get("uptime", "N/A"))
    except Exception as e:
        st.warning(f"Não foi possível carregar métricas da plataforma: {e}")
else:
    st.warning("⚠️ **Modo Fallback** - Plataforma unificada não disponível")

# Sidebar com navegação
st.sidebar.title("🎛️ Painel de Controle")

if platform:
    st.sidebar.success("✅ Plataforma Unificada")
else:
    st.sidebar.warning("⚠️ Modo Fallback")

page = st.sidebar.radio(
    "Selecione uma página",
    ["Visão Geral", "Plataforma Unificada", "Camadas", "Pipelines", "Prefect Flows", "Serviços", "ML Models", "Configuração"],
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

    styled_df = pipelines_df.style.map(color_status, subset=["status"])

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

# Página de Prefect Flows
elif page == "Prefect Flows":
    st.header("🔄 Monitoramento de Fluxos Prefect")

    # Status geral do Prefect
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔄 Fluxos Ativos", "12")
    with col2:
        st.metric("✅ Execuções Hoje", "47")
    with col3:
        st.metric("⚠️ Falhas", "2")
    with col4:
        st.metric("⏱️ Tempo Médio", "8m 32s")

    # Abas para diferentes visualizações
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Dashboard", "🔄 Fluxos", "📈 Métricas", "🚨 Alertas"]
    )

    with tab1:
        st.subheader("Status dos Principais Fluxos")

        flows_status = [
            {
                "Nome": "Medallion ETL Pipeline",
                "Status": "✅ Ativo",
                "Próxima Execução": "06:00",
                "Última Duração": "12m 45s",
            },
            {
                "Nome": "MLOps Training Pipeline",
                "Status": "⏸️ Pausado",
                "Próxima Execução": "Domingo 02:00",
                "Última Duração": "35m 20s",
            },
            {
                "Nome": "Real-time Monitoring",
                "Status": "✅ Ativo",
                "Próxima Execução": "A cada 5min",
                "Última Duração": "2m 15s",
            },
            {
                "Nome": "Data Lake Maintenance",
                "Status": "✅ Ativo",
                "Próxima Execução": "Sábado 03:00",
                "Última Duração": "18m 32s",
            },
        ]

        flows_df = pd.DataFrame(flows_status)
        st.dataframe(flows_df, use_container_width=True)

        # Gráfico de execuções por hora
        st.subheader("Execuções por Hora (Últimas 24h)")

        hours = list(range(24))
        executions = [
            3,
            2,
            1,
            0,
            0,
            0,
            8,
            5,
            7,
            12,
            15,
            18,
            22,
            19,
            16,
            14,
            11,
            9,
            7,
            5,
            4,
            3,
            2,
            1,
        ]

        hourly_data = pd.DataFrame({"Hora": hours, "Execuções": executions})
        chart = px.bar(
            hourly_data,
            x="Hora",
            y="Execuções",
            title="Distribuição de Execuções de Fluxos",
            color="Execuções",
            color_continuous_scale="viridis",
        )
        st.plotly_chart(chart, use_container_width=True)

    with tab2:
        st.subheader("Detalhes dos Fluxos")

        # Seletor de fluxo
        selected_flow = st.selectbox(
            "Selecione um fluxo:",
            [
                "Medallion ETL Pipeline",
                "MLOps Training Pipeline",
                "Real-time Monitoring",
                "Data Lake Maintenance",
            ],
        )

        if selected_flow == "Medallion ETL Pipeline":
            st.info("**Descrição:** Pipeline completo ETL com arquitetura Medallion")
            st.write("**Agendamento:** Diário às 06:00")
            st.write("**Duração Média:** 12m 45s")
            st.write("**Taxa de Sucesso:** 94.2%")

            # Histórico de execuções
            execution_history = [
                {
                    "Data": "2025-07-09 06:00",
                    "Status": "✅ Sucesso",
                    "Duração": "11m 23s",
                    "Registros": "125,430",
                },
                {
                    "Data": "2025-07-08 06:00",
                    "Status": "✅ Sucesso",
                    "Duração": "13m 15s",
                    "Registros": "132,891",
                },
                {
                    "Data": "2025-07-07 06:00",
                    "Status": "❌ Falha",
                    "Duração": "8m 42s",
                    "Registros": "0",
                },
                {
                    "Data": "2025-07-06 06:00",
                    "Status": "✅ Sucesso",
                    "Duração": "14m 07s",
                    "Registros": "118,765",
                },
            ]

            st.subheader("Histórico de Execuções")
            history_df = pd.DataFrame(execution_history)
            st.dataframe(history_df, use_container_width=True)

        elif selected_flow == "Real-time Monitoring":
            st.info("**Descrição:** Monitoramento em tempo real da plataforma DataLab")
            st.write("**Agendamento:** A cada 5 minutos")
            st.write("**Duração Média:** 2m 15s")
            st.write("**Taxa de Sucesso:** 99.1%")

            # Métricas em tempo real
            st.subheader("Métricas em Tempo Real")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tópicos Kafka", "3", "0")
            with col2:
                st.metric("Serviços Online", "6/6", "0")
            with col3:
                st.metric("Score Qualidade", "94%", "+2%")

    with tab3:
        st.subheader("Métricas de Performance")

        # Métricas de duração
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Duração por Tipo de Fluxo")
            duration_data = {
                "Tipo": ["ETL", "MLOps", "Monitoramento", "Manutenção"],
                "Duração Média (min)": [12.8, 35.4, 2.3, 18.6],
            }
            duration_df = pd.DataFrame(duration_data)
            chart = px.bar(
                duration_df,
                x="Tipo",
                y="Duração Média (min)",
                title="Duração Média por Tipo",
            )
            st.plotly_chart(chart, use_container_width=True)

        with col2:
            st.subheader("Taxa de Sucesso por Fluxo")
            success_data = {
                "Fluxo": ["Medallion ETL", "MLOps", "Monitoring", "Maintenance"],
                "Taxa de Sucesso (%)": [94.2, 87.5, 99.1, 91.8],
            }
            success_df = pd.DataFrame(success_data)
            chart = px.pie(
                success_df,
                names="Fluxo",
                values="Taxa de Sucesso (%)",
                title="Taxa de Sucesso",
            )
            st.plotly_chart(chart, use_container_width=True)

        # Tabela de recursos
        st.subheader("Uso de Recursos")
        resources_data = [
            {
                "Fluxo": "Medallion ETL",
                "CPU Médio": "1.2 cores",
                "Memória Média": "2.1 GB",
                "I/O": "Alto",
            },
            {
                "Fluxo": "MLOps Training",
                "CPU Médio": "2.8 cores",
                "Memória Média": "4.5 GB",
                "I/O": "Médio",
            },
            {
                "Fluxo": "Monitoring",
                "CPU Médio": "0.3 cores",
                "Memória Média": "0.5 GB",
                "I/O": "Baixo",
            },
            {
                "Fluxo": "Maintenance",
                "CPU Médio": "1.8 cores",
                "Memória Média": "3.2 GB",
                "I/O": "Alto",
            },
        ]
        resources_df = pd.DataFrame(resources_data)
        st.dataframe(resources_df, use_container_width=True)

    with tab4:
        st.subheader("🚨 Alertas e Notificações")

        # Alertas recentes
        alerts = [
            {
                "Timestamp": "2025-07-09 14:32",
                "Severidade": "⚠️ Warning",
                "Mensagem": "MLOps pipeline com duração acima da média",
                "Status": "Ativo",
            },
            {
                "Timestamp": "2025-07-09 12:15",
                "Severidade": "❌ Error",
                "Mensagem": "Falha na conexão com Kafka",
                "Status": "Resolvido",
            },
            {
                "Timestamp": "2025-07-09 08:45",
                "Severidade": "ℹ️ Info",
                "Mensagem": "Manutenção programada concluída",
                "Status": "Resolvido",
            },
            {
                "Timestamp": "2025-07-08 19:30",
                "Severidade": "⚠️ Warning",
                "Mensagem": "Uso de memória alto no Spark",
                "Status": "Monitorando",
            },
        ]

        alerts_df = pd.DataFrame(alerts)
        st.dataframe(alerts_df, use_container_width=True)

        # Configurações de alertas
        st.subheader("Configurações de Alertas")
        col1, col2 = st.columns(2)

        with col1:
            st.checkbox("Email notifications", value=True)
            st.checkbox("Slack notifications", value=False)
            st.checkbox("Teams notifications", value=False)

        with col2:
            st.slider("Threshold de duração (minutos)", 5, 60, 30)
            st.slider("Threshold de falhas consecutivas", 1, 10, 3)

        if st.button("💾 Salvar Configurações"):
            st.success("Configurações salvas com sucesso!")

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

elif page == "Plataforma Unificada":
    st.header("🌟 Plataforma Unificada - Gestão Centralizada")
    
    if not platform:
        st.error("❌ Plataforma unificada não está disponível. Certifique-se de que os módulos core estão instalados.")
        st.info("Para ativar a plataforma unificada, execute: `python setup.sh`")
        st.stop()
    
    # Tabs para diferentes aspectos da plataforma
    tab1, tab2, tab3, tab4 = st.tabs(["🏥 Health Check", "📊 Métricas", "🔄 Pipelines", "⚙️ Configuração"])
    
    with tab1:
        st.subheader("Health Check dos Serviços")
        
        if st.button("🔄 Verificar Health de Todos os Serviços"):
            with st.spinner("Verificando health dos serviços..."):
                try:
                    health_results = {}
                    services = ["spark", "kafka", "minio", "mlflow", "prefect", "jupyter"]
                    
                    for service in services:
                        try:
                            health = platform.check_service_health(service)
                            health_results[service] = health
                        except Exception as e:
                            health_results[service] = {"status": "error", "error": str(e)}
                    
                    # Mostrar resultados
                    for service, health in health_results.items():
                        status = health.get("status", "unknown")
                        if status == "healthy":
                            st.success(f"✅ {service.upper()}: Saudável")
                        elif status == "warning":
                            st.warning(f"⚠️ {service.upper()}: Atenção")
                        else:
                            st.error(f"❌ {service.upper()}: Problema")
                        
                        if "details" in health:
                            st.json(health["details"])
                            
                except Exception as e:
                    st.error(f"Erro ao verificar health: {e}")
    
    with tab2:
        st.subheader("Métricas da Plataforma")
        
        try:
            metrics = platform.get_metrics()
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Serviços Registrados", len(platform.service_registry))
            with col2:
                st.metric("Pipelines Ativos", metrics.get("active_pipelines", 0))
            with col3:
                st.metric("Erro Rate", f"{metrics.get('error_rate', 0):.1f}%")
            with col4:
                st.metric("Throughput", f"{metrics.get('throughput', 0)} req/s")
            
            # Gráfico de métricas
            if "historical_metrics" in metrics:
                df_metrics = pd.DataFrame(metrics["historical_metrics"])
                fig = px.line(df_metrics, x="timestamp", y="value", color="metric", 
                            title="Métricas da Plataforma ao Longo do Tempo")
                st.plotly_chart(fig, use_container_width=True)
            
            # Métricas detalhadas em JSON
            with st.expander("🔍 Métricas Detalhadas (JSON)"):
                st.json(metrics)
                
        except Exception as e:
            st.error(f"Erro ao carregar métricas: {e}")
    
    with tab3:
        st.subheader("Gestão de Pipelines")
        
        if orchestrator:
            # Mostrar pipelines registrados
            st.write("**Pipelines Registrados:**")
            
            try:
                pipelines = orchestrator.registered_pipelines
                if pipelines:
                    df_pipelines = pd.DataFrame([
                        {
                            "Nome": name,
                            "Tasks": len(pipeline["tasks"]),
                            "Schedule": pipeline.get("schedule", "Manual"),
                            "Enabled": pipeline.get("enabled", False),
                            "Último Sucesso": pipeline.get("success_count", 0),
                            "Falhas": pipeline.get("failure_count", 0)
                        }
                        for name, pipeline in pipelines.items()
                    ])
                    st.dataframe(df_pipelines, use_container_width=True)
                    
                    # Controles de pipeline
                    selected_pipeline = st.selectbox("Selecionar Pipeline", list(pipelines.keys()))
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("▶️ Executar Pipeline"):
                            st.info(f"Executando pipeline: {selected_pipeline}")
                    with col2:
                        if st.button("⏸️ Pausar Pipeline"):
                            st.info(f"Pipeline pausado: {selected_pipeline}")
                    with col3:
                        if st.button("📊 Ver Logs"):
                            st.info(f"Mostrando logs de: {selected_pipeline}")
                else:
                    st.info("Nenhum pipeline registrado")
                    
            except Exception as e:
                st.error(f"Erro ao carregar pipelines: {e}")
        else:
            st.warning("Orchestrator não disponível")
    
    with tab4:
        st.subheader("Configuração da Plataforma")
        
        if config_manager:
            try:
                # Mostrar configurações atuais
                st.write("**Configurações Atuais:**")
                
                # Configurações de exemplo (adapte conforme necessário)
                config_sections = ["platform", "services", "monitoring", "logging"]
                
                for section in config_sections:
                    with st.expander(f"📋 {section.title()}"):
                        try:
                            config = config_manager.get_config(section)
                            st.json(config)
                        except Exception as e:
                            st.warning(f"Não foi possível carregar config de {section}: {e}")
                
                # Formulário para atualizar configurações
                st.write("**Atualizar Configuração:**")
                with st.form("config_form"):
                    section = st.selectbox("Seção", config_sections)
                    key = st.text_input("Chave")
                    value = st.text_input("Valor")
                    
                    if st.form_submit_button("Atualizar"):
                        try:
                            # config_manager.update_config(section, key, value)
                            st.success(f"Configuração atualizada: {section}.{key} = {value}")
                        except Exception as e:
                            st.error(f"Erro ao atualizar configuração: {e}")
                            
            except Exception as e:
                st.error(f"Erro ao carregar configurações: {e}")
        else:
            st.warning("Gerenciador de configuração não disponível")

elif page == "Configuração":
    st.header("⚙️ Configuração do Sistema")
    
    st.write("**Configurações Gerais:**")
    
    # Configurações de refresh
    refresh_interval = st.slider("Intervalo de Refresh (segundos)", 30, 300, 60)
    st.write(f"Dados serão atualizados a cada {refresh_interval} segundos")
    
    # Configurações de logging
    log_level = st.selectbox("Nível de Log", ["DEBUG", "INFO", "WARNING", "ERROR"])
    
    # Configurações de notificações
    enable_notifications = st.checkbox("Habilitar Notificações", value=True)
    
    # Configurações da plataforma unificada
    st.write("**Configurações da Plataforma Unificada:**")
    
    if platform:
        st.success("✅ Plataforma unificada está ativa")
        
        # Mostrar informações do sistema
        with st.expander("📋 Informações do Sistema"):
            system_info = {
                "Plataforma Ativa": True,
                "Módulos Carregados": ["core.platform", "core.config", "core.orchestrator"],
                "Serviços Registrados": len(platform.service_registry) if platform else 0,
                "Timestamp": datetime.now().isoformat()
            }
            st.json(system_info)
    else:
        st.warning("⚠️ Plataforma unificada não está ativa")
        st.info("Para ativar a plataforma unificada:")
        st.code("""
# 1. Execute o setup
python setup.sh

# 2. Ou use o CLI
python datalab_cli.py platform start

# 3. Ou use o manager
python datalab_manager.py
        """)

# Rodapé
st.markdown("---")
st.markdown("🚀 DataLab Plataforma Unificada | Atualizado em: 9 de julho de 2025")
