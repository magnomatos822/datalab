# Streamlit no DataFlow Lab

## Visão Geral

O Streamlit é uma biblioteca de código aberto que transforma scripts Python em aplicativos web interativos. No DataFlow Lab, o Streamlit serve como a interface principal para visualização de dados e monitoramento do sistema, oferecendo dashboards interativos e aplicações analíticas que consomem dados processados da camada Gold.

Última atualização: **13 de maio de 2025**

## Componentes

O Streamlit no DataFlow Lab é implementado como:

1. **Contêiner Docker**: Executando o servidor Streamlit em uma imagem personalizada.
2. **Aplicações Python**: Scripts Python localizados no diretório `/app` que implementam as interfaces e visualizações.
3. **Dashboards de Monitoramento**: Visualizações e métricas para monitoramento da arquitetura de dados.

## Arquivos de Configuração

- **config/streamlit/Dockerfile**: Dockerfile personalizado para o serviço Streamlit.
- **app/app.py**: Aplicação principal do Streamlit.

## Como Usar

### Acessar os Dashboards

1. Inicie os serviços com `docker-compose up -d`
2. Acesse a interface web em `http://localhost:8501`
3. Navegue entre as diferentes visualizações usando o menu lateral
4. Não há autenticação configurada para o ambiente de desenvolvimento local. Para ambientes de produção, recomenda-se implementar autenticação.

### Variáveis de Ambiente Configuradas

O container Streamlit está configurado com as seguintes variáveis de ambiente para acesso aos outros serviços:

- MLFLOW_TRACKING_URI=http://mlflow:5000
- AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
- AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
- S3_ENDPOINT=http://minio:9000

### Dashboards Disponíveis

- **Visão Geral**: Métricas gerais do sistema e indicadores-chave
- **Monitor de Dados**: Estatísticas sobre os dados nas camadas Bronze, Silver e Gold
- **Qualidade de Dados**: Métricas de qualidade e validação dos dados
- **Pipeline Monitor**: Status e métricas de execução dos pipelines
- **Análises ML**: Resultados e performances dos modelos de machine learning

### Personalizar Dashboards

Para adicionar novas visualizações:

1. Crie um novo arquivo Python no diretório `/app` (ex: `meu_dashboard.py`)
2. Implemente sua visualização usando a API do Streamlit
3. Adicione-a ao arquivo `app.py` para aparecer no menu principal

```python
# Exemplo de um dashboard personalizado
import streamlit as st
import pandas as pd
import altair as alt
import pyminio
from app.medallion_architecture import MedallionData

# Título do Dashboard
st.title("Dashboard Personalizado")

# Conectar ao MinIO e carregar dados da camada Gold
medallion = MedallionData()
data = medallion.read_gold_data("meu_dataset")

# Converter para DataFrame
df = pd.DataFrame(data)

# Criar visualização
chart = alt.Chart(df).mark_bar().encode(
    x='categoria:N',
    y='valor:Q'
).properties(
    title='Análise por Categoria'
)

# Exibir no Streamlit
st.altair_chart(chart, use_container_width=True)

# Adicionar filtros interativos
categorias = st.multiselect("Filtrar por Categoria", df['categoria'].unique())
if categorias:
    df = df[df['categoria'].isin(categorias)]
    st.write(df)
```

## Integração com a Arquitetura Medallion

O Streamlit se integra com a arquitetura Medallion da seguinte forma:

1. Consome dados principalmente da camada Gold (dados refinados e prontos para análise)
2. Permite a exploração interativa dos resultados das transformações de dados
3. Fornece um front-end para monitorar a qualidade e o fluxo de dados através das camadas
4. Apresenta métricas e insights derivados do processamento dos dados

## Características Principais

1. **Dashboards Interativos**: Filtros, seletores e controles para explorar os dados
2. **Atualizações em Tempo Real**: Atualização automática das visualizações quando os dados mudam
3. **Monitor de Pipeline**: Visualização do status das execuções dos pipelines
4. **Integração com MLflow**: Exibição dos resultados dos experimentos de ML
5. **Alertas e Notificações**: Sistema de alerta para problemas nos dados ou nos pipelines

## Melhores Práticas

1. **Caching**: Use `@st.cache` para melhorar o desempenho de operações pesadas
2. **Reatividade**: Tire proveito da natureza reativa do Streamlit para criar interfaces dinâmicas
3. **Separação de Interfaces**: Crie arquivos separados para diferentes funcionalidades
4. **Estrutura Modular**: Reutilize componentes de visualização entre diferentes dashboards
5. **Controle de Acesso**: Implemente controle de acesso para informações sensíveis

## Solução de Problemas

### Problemas Comuns

1. **Dashboard lento**:
   - Implemente caching com `@st.cache`
   - Otimize as consultas ao MinIO
   - Reduza o volume de dados carregados

2. **Visualização incorreta dos dados**:
   - Verifique o formato dos dados retornados pelas consultas
   - Confirme que as transformações estão sendo aplicadas corretamente

3. **Erro de conexão com MinIO**:
   - Verifique as credenciais e configurações de conexão
   - Confirme que os buckets e os objetos existem

### Comandos Úteis

```bash
# Ver logs do Streamlit
docker logs streamlit

# Reiniciar o serviço Streamlit
docker-compose restart streamlit

# Acessar o contêiner para depuração
docker exec -it streamlit bash
```

## Recursos Adicionais

- [Documentação oficial do Streamlit](https://docs.streamlit.io)
- [Galeria de exemplos do Streamlit](https://streamlit.io/gallery)
- [Streamlit Components](https://streamlit.io/components)
