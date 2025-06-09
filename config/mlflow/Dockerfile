FROM bitnami/mlflow:2.22.0

USER root

# Instalando dependências necessárias
RUN pip install boto3 pymysql

# Criando diretório de trabalho do MLflow com permissões corretas
RUN mkdir -p /opt/mlflow && \
    chown -R 1001:1001 /opt/mlflow && \
    chmod 755 /opt/mlflow

# Verificando e configurando Python
RUN python3 --version
RUN which python3
RUN which mlflow

# Garantindo que o usuário 1001 possa escrever no diretório
RUN touch /opt/mlflow/mlflow.db && \
    chown 1001:1001 /opt/mlflow/mlflow.db

USER 1001
