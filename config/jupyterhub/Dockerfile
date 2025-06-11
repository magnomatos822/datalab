FROM jupyterhub/jupyterhub:4.0.2

USER root

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Configurar pip com timeouts maiores e parallelismo
RUN pip config set global.timeout 300
RUN pip config set install.trusted-host pypi.org
RUN pip config set install.trusted-host pypi.python.org
RUN pip config set install.trusted-host files.pythonhosted.org

# Instalar dependências básicas primeiro (sem PySpark para evitar timeout)
RUN pip install --no-cache-dir --retries 3 --timeout 300 \
    boto3 \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scikit-learn \
    requests

# Instalar dependências do JupyterHub
RUN pip install --no-cache-dir --retries 3 --timeout 300 \
    notebook \
    jupyterlab \
    jupyterhub-idle-culler \
    oauthenticator \
    dockerspawner

# Instalar MLflow e Prefect separadamente
RUN pip install --no-cache-dir --retries 3 --timeout 300 mlflow
RUN pip install --no-cache-dir --retries 3 --timeout 300 prefect

# Instalar PySpark por último com configurações otimizadas
RUN pip install --no-cache-dir --retries 5 --timeout 600 \
    --no-deps pyspark==3.5.5

# Instalar dependências do PySpark separadamente se necessário
RUN pip install --no-cache-dir py4j

# Configuração para conectar ao Spark
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Adiciona o diretório /.local/bin ao PATH
ENV PATH="/.local/bin:${PATH}"

# Copiar script de inicialização
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Criar diretórios necessários
RUN mkdir -p /home/jovyan/work

# Definir entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
