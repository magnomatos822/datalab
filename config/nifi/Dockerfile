FROM apache/nifi:2.4.0

USER root

# Instalar pacotes adicionais que podem ser úteis
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    jq \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar bibliotecas Python para integração
RUN pip3 install \
    boto3 \
    requests \
    pandas \
    prefect \
    pyspark

# Copiar scripts personalizados
COPY ./scripts/ /opt/nifi/nifi-current/scripts/

# Definir variáveis de ambiente para integração com outros serviços
ENV NIFI_SENSITIVE_PROPS_KEY=nifi-key \
    MINIO_ENDPOINT=http://minio:9000 \
    SPARK_MASTER_URL=spark://spark-master:7077 \
    MLFLOW_TRACKING_URI=http://mlflow:5000 \
    PREFECT_API_URL=http://prefect:4200/api

# Retornar ao usuário não-privilegiado para execução
USER nifi

# Manter o comando ENTRYPOINT padrão da imagem NiFi