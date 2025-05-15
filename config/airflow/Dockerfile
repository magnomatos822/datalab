FROM apache/airflow:2.8.1-python3.11

USER root

# Instalar dependências necessárias
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    netcat-traditional \
    gosu \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configurar variáveis de ambiente
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW_USER=airflow

# Copiar entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Criar diretório para scripts personalizados
RUN mkdir -p /scripts
COPY scripts/ /scripts/
RUN chmod -R +x /scripts/

# Criar diretórios do Airflow e configurar permissões
RUN mkdir -p ${AIRFLOW_HOME}/logs \
    && mkdir -p ${AIRFLOW_HOME}/dags \
    && mkdir -p ${AIRFLOW_HOME}/plugins \
    && mkdir -p ${AIRFLOW_HOME}/config \
    && chmod -R 777 ${AIRFLOW_HOME}/logs \
    && chmod -R 777 ${AIRFLOW_HOME}/dags \
    && chmod -R 777 ${AIRFLOW_HOME}/plugins \
    && chmod -R 777 ${AIRFLOW_HOME}/config

# Mudar para usuário airflow para instalar pacotes Python
USER ${AIRFLOW_USER}

# Instalação de requisitos Python adicionais
COPY --chown=airflow:root requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir apache-airflow-providers-apache-spark \
    && pip install --no-cache-dir apache-airflow-providers-amazon \
    && pip install --no-cache-dir apache-airflow-providers-postgres \
    && pip install --no-cache-dir apache-airflow-providers-apache-kafka

# Configuração final
WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT ["/entrypoint.sh"]