# DataFlow Lab

<div align="center">
  <img src="https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white" alt="Apache Spark">
  <img src="https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white" alt="MLflow">
  <img src="https://img.shields.io/badge/Prefect-024DFD?style=for-the-badge&logo=prefect&logoColor=white" alt="Prefect">
  <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter">
  <img src="https://img.shields.io/badge/MinIO-C72E49?style=for-the-badge&logo=minio&logoColor=white" alt="MinIO">
  <img src="https://img.shields.io/badge/Delta_Lake-00ADD8?style=for-the-badge&logo=delta&logoColor=white" alt="Delta Lake">
  <img src="https://img.shields.io/badge/Airbyte-615EFF?style=for-the-badge&logo=airbyte&logoColor=white" alt="Airbyte">
</div>

<br>

> Arquitetura moderna de Data Lakehouse com pipeline de dados para engenharia de dados e machine learning — processamento em camadas (Bronze, Silver, Gold), garantias ACID, time travel, monitoramento e orquestração.

## 📋 Sumário

- [DataFlow Lab](#dataflow-lab)
  - [📋 Sumário](#-sumário)
  - [🔭 Visão Geral](#-visão-geral)
  - [🏗️ Arquitetura](#️-arquitetura)
  - [🧩 Componentes](#-componentes)
    - [Armazenamento de Dados](#armazenamento-de-dados)
    - [Ingestão e ETL](#ingestão-e-etl)
    - [Processamento de Dados](#processamento-de-dados)
    - [Machine Learning](#machine-learning)
    - [Orquestração](#orquestração)
    - [Desenvolvimento](#desenvolvimento)
    - [Visualização](#visualização)
  - [🚀 Início Rápido](#-início-rápido)
    - [Pré-requisitos](#pré-requisitos)
    - [Instalação](#instalação)
  - [📂 Estrutura do Projeto](#-estrutura-do-projeto)
  - [🔄 Integração com Airbyte](#-integração-com-airbyte)
  - [📈 Analytics com Spark](#-analytics-com-spark)
  - [👥 Contribuição](#-contribuição)
  - [📄 Licença](#-licença)

## 🔭 Visão Geral

O DataFlow Lab é uma plataforma completa de Data Lakehouse para processamento de dados, abrangendo desde a ingestão de dados brutos até a criação de modelos de machine learning. A arquitetura implementa práticas modernas de engenharia de dados como processamento em camadas (Medallion: Bronze, Silver, Gold), transações ACID através do Delta Lake, rastreabilidade e reprodutibilidade.

Atualizado em: **12 de maio de 2025**

## 🏗️ Arquitetura

<pre>
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌────────────┐
│          │     │          │     │          │     │          │     │            │
│   RAW    │────▶│  BRONZE  │────▶│  SILVER  │────▶│   GOLD   │────▶│  ML MODELS │
│   DATA   │     │  LAYER   │     │  LAYER   │     │  LAYER   │     │            │
│          │     │          │     │          │     │          │     │            │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └────────────┘
      │                │                │                │                 │
      │                │                │                │                 │
      ▼                ▼                ▼                ▼                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                          ACID TRANSACTIONS (Delta Lake)                      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
      │                │                │                │                 │
      │                │                │                │                 │
      ▼                ▼                ▼                ▼                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                              DATA GOVERNANCE                                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
      │                │                │                │                 │
      │                │                │                │                 │
      ▼                ▼                ▼                ▼                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                          WORKFLOW ORCHESTRATION                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
</pre>

## 🧩 Componentes

O sistema é composto por vários componentes integrados que formam uma plataforma completa de Data Lakehouse:

### Armazenamento de Dados
- **[MinIO](docs/minio/README.md)**: Sistema de armazenamento de objetos compatível com Amazon S3
  - Console: [http://localhost:9001](http://localhost:9001) (admin/admin123)
  - API: [http://localhost:9000](http://localhost:9000)
  - Buckets: bronze, silver, gold (arquitetura Medallion)

### Ingestão e ETL
- **[Airbyte](docs/airbyte/README.md)**: Plataforma de integração de dados de código aberto
  - UI: [http://localhost:8000](http://localhost:8000) (airbyte/password)
  - Conectores para mais de 300 fontes de dados

### Processamento de Dados
- **[Apache Spark](docs/spark/README.md)**: Framework de processamento distribuído
  - Master UI: [http://localhost:8080](http://localhost:8080)
  - Worker UI: [http://localhost:8081](http://localhost:8081)
- **[Delta Lake](docs/spark/README.md#delta-lake)**: Camada de armazenamento que traz transações ACID para Spark
  - Formatos: delta (com garantias ACID)
  - Recursos: Time Travel, MERGE, Z-Order, Optimize

### Machine Learning
- **[MLflow](docs/mlflow/README.md)**: Plataforma para gerenciamento do ciclo de vida de ML
  - UI: [http://localhost:5000](http://localhost:5000)
  - Tracking, registros de modelos e serviço

### Orquestração
- **[Prefect](docs/prefect/README.md)**: Orquestrador de fluxos de dados
  - UI: [http://localhost:4200](http://localhost:4200)
  - Fluxos, tarefas e monitoramento

### Desenvolvimento
- **[JupyterHub](docs/jupyter/README.md)**: Ambiente de desenvolvimento interativo multi-usuário
  - UI: [http://localhost:8888](http://localhost:8888)
  - Notebooks para análise exploratória

### Visualização
- **[Streamlit](docs/streamlit/README.md)**: Framework para criação de aplicações de dados
  - UI: [http://localhost:8501](http://localhost:8501)
  - Dashboards interativos

## 🚀 Início Rápido

### Pré-requisitos

- Docker e Docker Compose instalados
- Git (opcional, para clonar o repositório)
- Recomendado: 8GB+ de RAM e 20GB+ de espaço em disco

### Instalação

1. Clone o repositório (ou baixe como ZIP):
   ```bash
   git clone https://github.com/seu-usuario/dataflow-lab.git
   cd dataflow-lab
   ```

2. Inicie os serviços:
   ```bash
   docker-compose up -d
   ```

3. Verifique se todos os serviços estão rodando:
   ```bash
   docker-compose ps
   ```

   Para verificar os logs de um serviço específico (por exemplo, Spark):
   ```bash
   docker-compose logs spark-master
   ```
   docker-compose ps
   ```

### URLs dos Serviços

| Serviço      | URL                   | Credenciais      |
| ------------ | --------------------- | ---------------- |
| MinIO        | http://localhost:9001 | admin/admin123   |
| Airbyte      | http://localhost:8000 | airbyte/password |
| Spark Master | http://localhost:8080 | -                |
| MLflow       | http://localhost:5000 | -                |
| Prefect UI   | http://localhost:4200 | -                |
| JupyterHub   | http://localhost:8888 | (token nos logs) |
| Streamlit    | http://localhost:8501 | -                |

## 📊 Uso do Sistema

### Arquitetura Medallion

Nossa implementação segue a arquitetura Medallion (também conhecida como multi-hop), organizada em três camadas principais:

1. **Bronze**: Dados brutos ingeridos sem modificações ou com mínimas transformações
   - Preserva os dados originais para auditoria e recuperação
   - Inclui metadados como hora de ingestão e fonte

2. **Silver**: Dados limpos, validados e transformados
   - Dados normalizados e estruturados
   - Valores nulos tratados e anomalias removidas
   - Esquema consistente e documentado

3. **Gold**: Dados refinados e agregados para consumo
   - Tabelas e views preparadas para análise
   - Dados agregados e modelados para casos de uso específicos
   - Otimizados para consulta e análise

### Transações ACID com Delta Lake

O projeto implementa o Delta Lake para fornecer garantias ACID (Atomicidade, Consistência, Isolamento, Durabilidade):

- **Atualizações incrementais (MERGE)**: Capacidade de atualizar registros existentes e inserir novos em uma única operação atômica
- **Time Travel**: Acesso a versões anteriores dos dados usando versão específica ou timestamp
- **Otimização de tabelas**: Compactação de arquivos pequenos e Z-Order para melhor performance de consulta
- **Schema Enforcement**: Validação automática de esquema para garantir qualidade dos dados
- **Gerenciamento de histórico**: Controle sobre retenção de versões antigas para economia de espaço

### Fluxo de Dados Típico

1. **Ingestão de Dados**: Coleta de dados de fontes diversas (APIs, bancos de dados, arquivos) usando Airbyte ou métodos personalizados
2. **Armazenamento Bronze**: Armazenamento dos dados brutos no formato Delta Lake (MinIO)
3. **Processamento Silver**: Limpeza e transformação com Apache Spark
4. **Refinamento Gold**: Agregações e modelagem para análise
5. **Modelagem**: Treinamento de modelos preditivos com rastreamento no MLflow
6. **Orquestração**: Automatização e agendamento de pipelines com Prefect
7. **Visualização**: Dashboards e aplicações com Streamlit

### Casos de Uso

O DataFlow Lab foi projetado para suportar diversos casos de uso:

- **ETL e ELT modernos**: Processamento de dados com estrutura de medallion
- **Machine Learning**: Treinamento e implementação de modelos com MLflow
- **Análise financeira**: Processamento de séries temporais e dados financeiros
- **Processamento de logs**: Análise de logs e telemetria
- **Integração de dados**: Unificação de fontes de dados heterogêneas
- **Analytics em tempo real**: Processamento de streaming com Spark Structured Streaming

### Exemplos Práticos

Consulte nossos exemplos para casos de uso comuns:

- `/app/medallion_example.py`: Exemplo completo da arquitetura Medallion com Delta Lake
- `/app/medallion_prefect_flow.py`: Orquestração do pipeline Medallion usando Prefect
- `/app/analytics.py`: Análises avançadas com Apache Spark
- `/notebooks/magnomatos822/amazon.ipynb`: Análise de dados financeiros da Amazon

Para executar o exemplo da arquitetura Medallion:

```bash
docker exec -it spark-master python /spark-apps/medallion_prefect_flow.py
```

## 📂 Estrutura do Projeto

```
dataflow-lab/
│
├── docker-compose.yml      # Definição dos serviços Docker
├── jupyterhub_config.py    # Configuração do JupyterHub
├── README.md               # Este arquivo
├── LICENSE                 # Licença do projeto
├── requirements.txt        # Dependências Python (incluindo delta-spark)
│
├── app/                    # Código Python da aplicação
│   ├── airbyte_integration.py     # Integração com Airbyte
│   ├── airbyte_monitoring.py      # Monitoramento de conexões Airbyte
│   ├── airbyte_prefect_deployment.py  # Integração Airbyte + Prefect
│   ├── analytics.py               # Funções analíticas com Spark
│   ├── app.py                     # Aplicação principal
│   ├── ingestion.py               # Módulo de ingestão de dados
│   ├── medallion_architecture.py  # Implementação da arquitetura Medallion
│   ├── medallion_example.py       # Exemplo de uso
│   ├── medallion_prefect_flow.py  # Fluxos Prefect para orquestração
│   └── processor.py               # Processamento de dados com Spark
│
├── docs/                   # Documentação detalhada
│   ├── airbyte/            # Documentação do Airbyte
│   ├── minio/              # Documentação do MinIO
│   ├── spark/              # Documentação do Apache Spark e Delta Lake
│   ├── mlflow/             # Documentação do MLflow
│   ├── prefect/            # Documentação do Prefect
│   └── jupyter/            # Documentação do Jupyter
│
├── notebooks/              # Jupyter notebooks de exemplo
│   ├── magnomatos822/      # Notebooks do usuário
│   │   ├── amazon.ipynb    # Análise de dados da Amazon
│   │   └── teste.ipynb     # Notebook de testes
│   └── tutorials/          # Notebooks de tutoriais
│
├── config/                 # Arquivos de configuração
│   ├── minio/              # Configurações do MinIO
│   ├── spark/              # Configurações do Spark
│   └── nginx/              # Configurações do NGINX
│
├── data/                   # Diretório para armazenar dados
│   ├── jupyter/            # Dados do JupyterHub
│   ├── minio/              # Buckets do MinIO (bronze, silver, gold)
│   ├── mlflow/             # Dados do MLflow
│   ├── prefect/            # Dados do Prefect
│   ├── spark/              # Logs e dados do Spark
│   └── streamlit/          # Dados do Streamlit
│
├── flows/                  # Definições de fluxos Prefect
├── mlruns/                 # Diretório para armazenar artefatos do MLflow
│   └── models/             # Modelos treinados
│
└── models/                 # Modelos exportados
```

## 🔄 Integração com Airbyte

O DataFlow Lab integra-se com o Airbyte para ingestão de dados de diversas fontes. Os principais componentes de integração são:

- **airbyte_integration.py**: Fornece APIs para interagir com o Airbyte
- **airbyte_monitoring.py**: Monitora o status das conexões e sincronizações
- **airbyte_prefect_deployment.py**: Integra fluxos de dados do Airbyte com orquestração Prefect

Para configurar uma nova fonte de dados:

1. Acesse a UI do Airbyte em http://localhost:8000
2. Configure a fonte de dados desejada
3. Configure o destino como MinIO (Bronze layer)
4. Crie uma conexão entre fonte e destino
5. Use os scripts de integração para automatizar o processo

## 📈 Analytics com Spark

O componente de analytics (`app/analytics.py`) fornece funções para análise de dados avançada:

- Análise de séries temporais
- Detecção de anomalias
- Análise de sentimento
- Processamento de linguagem natural
- Análises preditivas

Exemplo de uso:

```python
from app.analytics import TimeSeriesAnalyzer

# Carregar dados da camada Gold
data = spark.read.format("delta").load("s3a://gold/stock_data")

# Realizar análise de séries temporais
analyzer = TimeSeriesAnalyzer(data)
results = analyzer.analyze(metric="close_price", period=30)
forecast = analyzer.forecast(days=7)
```

## 👥 Contribuição

Contribuições são bem-vindas! Por favor, siga estas etapas para contribuir:

1. Fork o repositório
2. Crie um branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas alterações (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para o branch (`git push origin feature/nova-funcionalidade`)
5. Crie um Pull Request

## 📄 Licença

Este projeto é licenciado sob a [GNU General Public License v3.0](LICENSE) - veja o arquivo LICENSE para detalhes.
