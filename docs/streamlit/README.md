# Streamlit - Dashboards e Visualizações Interativas

<div align="center">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
</div>

> Versão: 1.45.0

## O que é Streamlit?

Streamlit é uma biblioteca Python de código aberto que facilita a criação de aplicações web interativas e dashboards para visualização de dados, machine learning e análises científicas. Ao contrário de frameworks tradicionais de desenvolvimento web, o Streamlit permite criar interfaces sofisticadas com código Python puro, sem necessidade de conhecimentos em HTML, CSS ou JavaScript.

No DataFlow Lab, o Streamlit serve como a camada de visualização, conectando-se aos dados processados nas camadas Gold e Silver para criar dashboards e interfaces analíticas.

## Características Principais

- **Simplicidade**: Crie apps com poucas linhas de código Python
- **Desenvolvimento Ágil**: Hot-reload automático durante o desenvolvimento
- **Componentes Interativos**: Widgets, gráficos e filtros interativos
- **Personalização**: Temas, layouts e estilos configuráveis
- **Cache Inteligente**: Cache automático para otimizar performance
- **Integração de Dados**: Conexão fácil com diversas fontes de dados

## Como Acessar

O Streamlit está disponível em:

- **URL**: [http://localhost:8501](http://localhost:8501)

## Estrutura do Streamlit no DataFlow Lab

```
config/streamlit/
├── Dockerfile          # Configuração do container
└── requirements.txt    # Dependências específicas do Streamlit

app/
├── app.py              # Aplicação principal do Streamlit
└── analytics.py        # Funções analíticas utilizadas nos dashboards
```

## Exemplos de Uso

### Aplicação Básica

O arquivo `app.py` contém a aplicação principal do Streamlit:

```python
import streamlit as st
import pandas as pd
import plotly.express as px
from pyspark.sql import SparkSession

# Título e descrição
st.set_page_config(
    page_title="DataFlow Lab Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("🔍 DataFlow Lab Analytics")
st.subheader("Dashboard interativo para análise de dados")

# Inicializar conexão com Spark
@st.cache_resource
def get_spark_session():
    return SparkSession.builder \
        .appName("StreamlitDashboard") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "admin") \
        .config("spark.hadoop.fs.s3a.secret.key", "admin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

spark = get_spark_session()

# Carregar dados da camada Gold
@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_gold_data(domain, dataset):
    path = f"s3a://gold/{domain}/{dataset}"
    df = spark.read.format("delta").load(path)
    return df.toPandas()

# Interface para selecionar dados
st.sidebar.header("Filtros")

domain = st.sidebar.selectbox(
    "Domínio de Análise",
    ["analytics_domain1", "analytics_domain2", "ml_features"]
)

datasets = {
    "analytics_domain1": ["dashboard1", "sales_overview", "user_metrics"],
    "analytics_domain2": ["view1", "performance_analysis"],
    "ml_features": ["feature_store"]
}

dataset = st.sidebar.selectbox(
    "Dataset",
    datasets[domain]
)

# Carregar os dados selecionados
try:
    with st.spinner("Carregando dados..."):
        df = load_gold_data(domain, dataset)
    
    # Mostrar informações básicas
    st.markdown(f"### Dataset: {dataset}")
    st.write(f"**Registros:** {len(df)}")
    st.write(f"**Colunas:** {', '.join(df.columns)}")
    
    # Visualizar os dados
    tab1, tab2, tab3 = st.tabs(["📊 Visualização", "🔢 Dados Brutos", "📈 Estatísticas"])
    
    with tab1:
        # Gráficos automáticos baseados nos tipos de dados
        num_columns = df.select_dtypes(include=['number']).columns
        if len(num_columns) >= 2:
            x_col = st.selectbox("Eixo X:", num_columns)
            y_col = st.selectbox("Eixo Y:", [c for c in num_columns if c != x_col])
            
            chart_type = st.radio(
                "Tipo de Gráfico:",
                ["Dispersão", "Linha", "Barra", "Histograma"]
            )
            
            if chart_type == "Dispersão":
                fig = px.scatter(df, x=x_col, y=y_col)
            elif chart_type == "Linha":
                fig = px.line(df, x=x_col, y=y_col)
            elif chart_type == "Barra":
                fig = px.bar(df, x=x_col, y=y_col)
            else:
                fig = px.histogram(df, x=x_col)
                
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.dataframe(df)
        
    with tab3:
        st.write(df.describe())
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")

# Métricas em destaque
if "analytics_domain1" in domain:
    st.markdown("### 📌 Métricas Principais")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total de Vendas", 
            value=f"R$ {df['valor'].sum():,.2f}" if 'valor' in df.columns else "N/A",
            delta="+12.5%" if 'valor' in df.columns else None
        )
        
    with col2:
        st.metric(
            label="Média", 
            value=f"{df[num_columns[0]].mean():.2f}" if len(num_columns) > 0 else "N/A"
        )
        
    with col3:
        st.metric(
            label="Máximo", 
            value=f"{df[num_columns[0]].max():.2f}" if len(num_columns) > 0 else "N/A"
        )

# Exportar dados
st.sidebar.header("Exportar")

export_format = st.sidebar.selectbox(
    "Formato de Exportação",
    ["CSV", "Excel", "JSON"]
)

if st.sidebar.button("Exportar Dados"):
    if export_format == "CSV":
        csv = df.to_csv(index=False)
        st.sidebar.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{dataset}.csv",
            mime="text/csv"
        )
    elif export_format == "Excel":
        # Configuração para Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
        st.sidebar.download_button(
            label="Download Excel",
            data=output.getvalue(),
            file_name=f"{dataset}.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        json_data = df.to_json(orient="records")
        st.sidebar.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"{dataset}.json",
            mime="application/json"
        )

# Rodapé
st.sidebar.markdown("---")
st.sidebar.markdown("### Sobre")
st.sidebar.info(
    """
    Este dashboard é parte do DataFlow Lab - um ambiente completo para
    processamento de dados em camadas (Bronze, Silver, Gold) integrado
    com ferramentas modernas de Big Data.
    
    [Documentação](/) | [Código Fonte](/)
    """
)
```

## Integrações com o DataFlow Lab

### Integração com Delta Lake (MinIO)

```python
# Acesso aos dados armazenados no MinIO via Delta Lake
import streamlit as st
from pyspark.sql import SparkSession

@st.cache_resource
def get_spark():
    return SparkSession.builder \
        .appName("Streamlit-MinIO") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "admin") \
        .config("spark.hadoop.fs.s3a.secret.key", "admin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

spark = get_spark()

# Leitura de dados Delta armazenados no MinIO
def read_delta_table(path):
    return spark.read.format("delta").load(path)

# Uso no Streamlit
bronze_data = read_delta_table("s3a://bronze/raw_data_source1/table1")
silver_data = read_delta_table("s3a://silver/clean_data_domain1/table1")
gold_data = read_delta_table("s3a://gold/analytics_domain1/dashboard1")

# Exibir dados
st.write("### Dados da Camada Gold")
st.write(gold_data.limit(1000).toPandas())
```

### Integração com MLflow

```python
# Visualizar modelos do MLflow
import streamlit as st
import mlflow
import pandas as pd
from mlflow.tracking import MlflowClient

# Configurar conexão com MLflow
@st.cache_resource
def get_mlflow_client():
    mlflow.set_tracking_uri("http://mlflow:5000")
    return MlflowClient()

client = get_mlflow_client()

# Listar experimentos
st.title("📊 MLflow Explorer")

experiments = client.search_experiments()
experiment_names = [exp.name for exp in experiments]
selected_experiment = st.selectbox("Selecione um experimento:", experiment_names)

# Obter ID do experimento selecionado
experiment_id = None
for exp in experiments:
    if exp.name == selected_experiment:
        experiment_id = exp.experiment_id
        break

# Listar runs do experimento selecionado
if experiment_id:
    runs = client.search_runs(experiment_ids=[experiment_id])
    
    run_data = []
    for run in runs:
        run_data.append({
            "Run ID": run.info.run_id,
            "Status": run.info.status,
            "Start Time": pd.to_datetime(run.info.start_time, unit='ms'),
            "End Time": pd.to_datetime(run.info.end_time, unit='ms') if run.info.end_time else None,
            **{k: v for k, v in run.data.metrics.items()},
            **{f"param_{k}": v for k, v in run.data.params.items()}
        })
    
    if run_data:
        df_runs = pd.DataFrame(run_data)
        st.write("### Experimentos")
        st.dataframe(df_runs)
        
        # Selecionar um run para detalhes
        selected_run_id = st.selectbox("Selecione um run para ver detalhes:", df_runs["Run ID"])
        
        if selected_run_id:
            st.write("### Detalhes do Run")
            run = client.get_run(selected_run_id)
            
            # Mostrar métricas
            st.write("#### Métricas")
            metrics = run.data.metrics
            for key, value in metrics.items():
                st.metric(key, value)
            
            # Mostrar parâmetros
            st.write("#### Parâmetros")
            params = run.data.params
            st.json(params)
            
            # Mostrar artefatos
            st.write("#### Artefatos")
            artifacts = client.list_artifacts(selected_run_id)
            for artifact in artifacts:
                st.write(f"- {artifact.path} ({artifact.file_size} bytes)")
```

## Desenvolvimento de Dashboards

### Estrutura Recomendada

Organize seus dashboards Streamlit seguindo esta estrutura:

1. **Página principal (app.py)**: Dashboard principal com visão geral
2. **Páginas temáticas**: Dashboards específicos para cada área de negócio
3. **Componentes reutilizáveis**: Funções para gráficos e widgets comuns

### Sistema de Múltiplas Páginas

Configuração de múltiplas páginas usando a estrutura nativa do Streamlit:

```
app/
├── pages/
│   ├── 01_📈_Sales_Dashboard.py
│   ├── 02_👥_Customer_Analysis.py
│   └── 03_🧮_Inventory_Metrics.py
└── app.py  # Página principal
```

### Componentes Reutilizáveis

Crie um módulo de componentes para reutilização:

```python
# components.py
import streamlit as st
import plotly.express as px

def metric_card(title, value, delta=None, delta_color="normal"):
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def time_series_chart(df, date_column, value_column, title, color_column=None):
    fig = px.line(
        df,
        x=date_column,
        y=value_column,
        color=color_column,
        title=title
    )
    return fig

def data_filter_sidebar(df, date_column=None, category_columns=[]):
    filters = {}
    
    st.sidebar.header("Filtros")
    
    # Filtro de data
    if date_column and date_column in df.columns:
        date_min = df[date_column].min().date()
        date_max = df[date_column].max().date()
        
        filters["date_range"] = st.sidebar.date_input(
            "Período",
            value=(date_min, date_max)
        )
    
    # Filtros categóricos
    for col in category_columns:
        if col in df.columns:
            options = ["Todos"] + sorted(df[col].unique().tolist())
            filters[col] = st.sidebar.selectbox(f"Filtro por {col}", options)
    
    return filters
```

## Personalização e Temas

### Configuração Personalizada

Para configurar a aparência do Streamlit, crie um arquivo `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#0076BE"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[browser]
gatherUsageStats = false

[server]
enableCORS = false
enableXsrfProtection = true

[runner]
magicEnabled = true
```

### CSS Personalizado

Adicione estilos CSS personalizados ao seu app:

```python
st.markdown("""
<style>
    .reportview-container .main {
        background-color: #f8f8fa;
    }
    .custom-metric-card {
        border-radius: 10px;
        padding: 1.5rem;
        background-color: #ffffff;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    .custom-metric-card h3 {
        color: #0076BE;
        font-size: 1.2rem;
    }
    .custom-metric-card .value {
        font-size: 2rem;
        font-weight: bold;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)
```

## Otimizações de Performance

### Cache Inteligente

O Streamlit oferece três decoradores para cache:

1. `@st.cache_data`: Para funções que retornam dados (pandas, numpy, etc.)
2. `@st.cache_resource`: Para recursos compartilhados (conexões DB, modelos)
3. `@st.cache_data.clear()`: Para limpar cache quando necessário

Exemplo:

```python
@st.cache_data(ttl=300)  # Invalidar após 5 minutos
def fetch_gold_data():
    # Código que pode ser demorado
    return spark.read.format("delta").load("s3a://gold/...").toPandas()

# Uso em outro lugar
if st.button("Recarregar Dados"):
    # Forçar recarregamento
    st.cache_data.clear()
    data = fetch_gold_data()
else:
    data = fetch_gold_data()
```

### Processamento Assíncrono

Use processamento assíncrono para operações longas:

```python
import asyncio
import streamlit as st

@st.cache_data
async def long_running_task():
    await asyncio.sleep(5)  # Simulando processamento longo
    return "Resultado do processamento"

st.title("Processamento Assíncrono")

if "resultado" not in st.session_state:
    st.session_state.resultado = None
    st.session_state.processando = False

if st.button("Iniciar Processamento"):
    st.session_state.processando = True
    with st.spinner("Processando dados..."):
        # Executar de forma assíncrona
        st.session_state.resultado = asyncio.run(long_running_task())
    st.session_state.processando = False

if st.session_state.resultado:
    st.success("Processamento concluído!")
    st.write(st.session_state.resultado)
```

## Deployment e Configuração

### Configuração Docker

O Streamlit já está configurado no DataFlow Lab via Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expor porta do Streamlit
EXPOSE 8501

# Comando para iniciar o Streamlit
CMD ["streamlit", "run", "/app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Configurações de Ambiente

As seguintes variáveis de ambiente são configuradas:

- `MLFLOW_TRACKING_URI=http://mlflow:5000`
- `AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}`
- `AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}`
- `S3_ENDPOINT=http://minio:9000`

## Melhores Práticas

1. **Estrutura Organizada**:
   - Divida apps grandes em múltiplas páginas
   - Use componentes reutilizáveis

2. **Performance**:
   - Cache dados adequadamente com `@st.cache_data`
   - Use recursos compartilhados com `@st.cache_resource`

3. **UX/UI**:
   - Mantenha interfaces simples e intuitivas
   - Use layouts responsivos (st.columns)
   - Forneça filtros interativos para exploração

4. **Dados**:
   - Inclua exportação de dados em formatos comuns
   - Mostre metadados importantes (fontes, datas de atualização)

5. **Manutenção**:
   - Documente componentes complexos
   - Use tratamento de erros robusto
   - Inclua logs para depuração

## Recursos Adicionais

- [Documentação Oficial Streamlit](https://docs.streamlit.io/)
- [Galeria de Exemplos Streamlit](https://streamlit.io/gallery)
- [Streamlit Components](https://streamlit.io/components)
- [GitHub do Streamlit](https://github.com/streamlit/streamlit)
- [Fórum da Comunidade](https://discuss.streamlit.io/)
