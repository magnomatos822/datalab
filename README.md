# DataFlow Lab

<div align="center">
  <img src="https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white" alt="Apache Spark">
  <img src="https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white" alt="MLflow">
  <img src="https://img.shields.io/badge/Prefect-024DFD?style=for-the-badge&logo=prefect&logoColor=white" alt="Prefect">
  <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter">
  <img src="https://img.shields.io/badge/MinIO-C72E49?style=for-the-badge&logo=minio&logoColor=white" alt="MinIO">
  <img src="https://img.shields.io/badge/Delta_Lake-00ADD8?style=for-the-badge&logo=delta&logoColor=white" alt="Delta Lake">
  <img src="https://img.shields.io/static/v1?style=for-the-badge&message=Apache+NiFi&color=728E9B&logo=Apache+NiFi&logoColor=FFFFFF&label=" alt="Apache NiFi">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Airflow-017C74?style=for-the-badge&logo=apache-airflow&logoColor=white" alt="Apache Airflow">
  <img src="https://img.shields.io/badge/Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white" alt="Apache Kafka">
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
    - [URLs dos Serviços](#urls-dos-serviços)
  - [📂 Estrutura do Projeto](#-estrutura-do-projeto)
  - [📊 Uso do Sistema](#-uso-do-sistema)
    - [Arquitetura Medallion](#arquitetura-medallion)
    - [Transações ACID com Delta Lake](#transações-acid-com-delta-lake)
    - [Fluxo de Dados Típico](#fluxo-de-dados-típico)
    - [Casos de Uso](#casos-de-uso)
    - [Exemplos Práticos](#exemplos-práticos)
  - [🔄 Integração com Apache NiFi](#-integração-com-apache-nifi)
  - [📈 Analytics com Spark e Kafka](#-analytics-com-spark-e-kafka)
  - [👥 Contribuição](#-contribuição)
  - [📄 Licença](#-licença)

## 🔭 Visão Geral

O DataFlow Lab é uma plataforma completa de Data Lakehouse para processamento de dados, abrangendo desde a ingestão de dados brutos até a criação de modelos de machine learning. A arquitetura implementa práticas modernas de engenharia de dados como processamento em camadas (Medallion: Bronze, Silver, Gold), transações ACID através do Delta Lake, rastreabilidade e reprodutibilidade.

Atualizado em: **14 de maio de 2025**

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
│                         STREAMING (Kafka/Spark)                              │
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
  - **Versão**: 2025-04-22

### Ingestão e ETL
- **[Apache NiFi](docs/nifi/README.md)**: Plataforma para automação de fluxos de dados
  - UI: [https://localhost:8443](https://localhost:8443) (nifi/senha-configurada)
  - Drivers JDBC pré-instalados para PostgreSQL, MySQL, Oracle
  - **Versão**: 2.4.0

### Processamento de Dados
- **[Apache Spark](docs/spark/README.md)**: Framework de processamento distribuído
  - Master UI: [http://localhost:8080](http://localhost:8080)
  - Worker UI: [http://localhost:8081](http://localhost:8081)
  - **Versão**: 3.5.5
- **[Delta Lake](docs/spark/README.md#delta-lake)**: Camada de armazenamento que traz transações ACID para Spark
  - Formatos: delta (com garantias ACID)
  - Recursos: Time Travel, MERGE, Z-Order, Optimize
  - **Versão**: 3.3.1
- **[Apache Kafka](docs/kafka/README.md)**: Plataforma de streaming distribuído
  - Broker: [localhost:9092](localhost:9092)
  - Interface: [http://localhost:8090](http://localhost:8090)
  - **Versão**: 7.5.0

### Machine Learning
- **[MLflow](docs/mlflow/README.md)**: Plataforma para gerenciamento do ciclo de vida de ML
  - UI: [http://localhost:5000](http://localhost:5000)
  - Tracking, registros de modelos e serviço
  - Integração com MinIO para armazenamento de artefatos
  - **Versão**: 2.22.0

### Orquestração
- **[Prefect](docs/prefect/README.md)**: Orquestrador de fluxos de dados
  - UI: [http://localhost:4200](http://localhost:4200)
  - Fluxos, tarefas e monitoramento
  - **Versão**: 3.4.1

### Desenvolvimento
- **[JupyterHub](docs/jupyterhub/README.md)**: Ambiente de desenvolvimento interativo multi-usuário
  - UI: [http://localhost:8888](http://localhost:8888)
  - Notebooks para análise exploratória
  - **Versão**: 5.3.0

### Visualização
- **[Streamlit](docs/streamlit/README.md)**: Framework para criação de aplicações de dados
  - UI: [http://localhost:8501](http://localhost:8501)
  - Dashboards interativos
  - **Versão**: 1.45.0

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

2. Crie um arquivo `.env` com as credenciais necessárias:
   ```bash
   echo "MINIO_ROOT_USER=admin" > .env
   echo "MINIO_ROOT_PASSWORD=admin123" >> .env
   echo "AWS_ACCESS_KEY_ID=admin" >> .env
   echo "AWS_SECRET_ACCESS_KEY=admin123" >> .env
   ```

3. Inicie os serviços:
   ```bash
   docker-compose up -d
   ```

4. Verifique se todos os serviços estão rodando:
   ```bash
   docker-compose ps
   ```

   Para verificar os logs de um serviço específico (por exemplo, Spark):
   ```bash
   docker-compose logs spark-master
   ```

### URLs dos Serviços

| Serviço      | URL                      | Credenciais      |
| ------------ | ------------------------ | ---------------- |
| MinIO        | http://localhost:9001    | admin/admin123   |
| Apache NiFi  | https://localhost:8443   | nifi/senha-config |
| Spark Master | http://localhost:8080    | -                |
| MLflow       | http://localhost:5000    | -                |
| Prefect UI   | http://localhost:4200    | -                |
| JupyterHub   | http://localhost:8888    | (token nos logs) |
| Streamlit    | http://localhost:8501    | -                |
| Kafka UI     | http://localhost:8090    | -                |

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
│   ├── analytics.py               # Funções analíticas com Spark
│   ├── app.py                     # Aplicação principal
│   ├── medallion_architecture.py  # Implementação da arquitetura Medallion
│   ├── medallion_example.py       # Exemplo de uso
│   ├── medallion_prefect_flow.py  # Fluxos Prefect para orquestração
│   ├── mlflow.py                  # Integrações com MLflow
│   └── tutorial.py                # Tutoriais e exemplos
│
├── docs/                   # Documentação detalhada
│   ├── airflow/            # Documentação do Airflow
│   ├── jupyterhub/         # Documentação do JupyterHub
│   ├── kafka/              # Documentação do Kafka
│   ├── minio/              # Documentação do MinIO
│   ├── mlflow/             # Documentação do MLflow
│   ├── nifi/               # Documentação do NiFi
│   ├── prefect/            # Documentação do Prefect
│   ├── spark/              # Documentação do Apache Spark e Delta Lake
│   └── streamlit/          # Documentação do Streamlit
│
├── notebooks/              # Jupyter notebooks de exemplo
│   ├── jupyterhub_credentials.ipynb # Informações de credenciais
│   ├── magnomatos822/      # Notebooks do usuário
│   │   └── amazon.ipynb    # Análise de dados da Amazon
│   ├── nifi_tutorials/     # Tutoriais do NiFi
│   └── retail_analysis/    # Análise de dados de varejo
│
├── config/                 # Arquivos de configuração
│   ├── airflow/            # Configurações do Airflow
│   ├── jupyterhub/         # Configurações do JupyterHub
│   ├── mlflow/             # Configurações do MLflow
│   ├── spark/              # Configurações do Spark
│   │   └── conf/           # Arquivos de configuração do Spark
│   └── streamlit/          # Configurações do Streamlit
│
├── data/                   # Diretório para armazenar dados
│   ├── airflow/            # Dados do Airflow
│   ├── jupyter/            # Dados do JupyterHub
│   ├── minio/              # Buckets do MinIO (bronze, silver, gold)
│   ├── mlflow/             # Dados do MLflow
│   ├── nifi/               # Dados do NiFi
│   ├── postgres/           # Dados do PostgreSQL
│   ├── prefect/            # Dados do Prefect
│   └── spark/              # Logs e dados do Spark
│
├── flows/                  # Definições de fluxos Prefect
├── mlruns/                 # Diretório para armazenar artefatos do MLflow
│   └── models/             # Modelos treinados
│
├── models/                 # Modelos exportados
│
├── nifi/                   # Recursos para Apache NiFi
│   ├── drivers/            # Drivers JDBC organizados por tipo de banco
│   └── jdbc/               # Drivers JDBC gerais
│
└── scripts/                # Scripts utilitários
    ├── download_spark_jars.sh  # Script para baixar JARs do Spark
    └── init_minio.sh      # Script para inicialização do MinIO
```

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

1. **Ingestão de Dados**: Coleta de dados de fontes diversas (APIs, bancos de dados, arquivos) usando NiFi
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
- **Analytics em tempo real**: Processamento de streaming com Kafka e Spark Structured Streaming

### Exemplos Práticos

Consulte nossos exemplos para casos de uso comuns:

- `/app/medallion_example.py`: Exemplo completo da arquitetura Medallion com Delta Lake
- `/app/medallion_prefect_flow.py`: Orquestração do pipeline Medallion usando Prefect
- `/app/analytics.py`: Análises avançadas com Apache Spark
- `/notebooks/magnomatos822/amazon.ipynb`: Análise de dados financeiros da Amazon

Para executar o exemplo da arquitetura Medallion:

```bash
docker exec -it spark-master python /opt/spark-apps/medallion_prefect_flow.py
```

## 🔄 Integração com Apache NiFi

O DataFlow Lab utiliza o Apache NiFi (2.4.0) para ingestão e transformação de dados. As principais características da integração são:

- **Interface segura**: Acesso via HTTPS em https://localhost:8443
- **Drivers pré-configurados**: PostgreSQL, MySQL, MS SQL Server e Oracle
- **Fluxos de exemplo**: Disponíveis na pasta `nifi/templates`
- **Organização por tipo**: Drivers organizados por tipo de banco de dados

Para acessar o Apache NiFi:

1. Acesse [https://localhost:8443/nifi](https://localhost:8443/nifi)
2. Utilize as credenciais configuradas (padrão: nifi/senha-configurada)
3. Importe templates ou crie novos fluxos

Exemplo de NiFi para enviar dados para o Data Lake:
```
GetFile -> ExtractText -> ConvertJSONtoSQL -> PutS3Object
```

## 📈 Analytics com Spark e Kafka

O componente de analytics (`app/analytics.py`) fornece funções para análise de dados avançada, agora com integrações Kafka:

- **Análise em tempo real**: Processamento de eventos em tempo real com Kafka
- **Análise de séries temporais**: Previsões e detecção de tendências
- **Detecção de anomalias**: Identificação de padrões incomuns
- **Análise de sentimento**: Processamento de texto com NLP
- **Analytics preditivos**: Modelos de machine learning avançados

Exemplo de uso com Kafka:

```python
from app.analytics import StreamProcessor

# Configurar processador de streaming
processor = StreamProcessor(
    bootstrap_servers="kafka:9092",
    input_topic="raw_data",
    output_topic="processed_data"
)

# Definir transformação
def transform(df):
    return df.withColumn("processed_value", df.value * 2)

# Iniciar processamento
processor.start_processing(transform)
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
