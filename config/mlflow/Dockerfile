FROM bitnami/mlflow:2.22.0

USER root

# Instalando dependências necessárias
RUN pip install boto3 pymysql

# Na imagem bitnami/mlflow, o Python pode estar em /opt/bitnami/python/bin/python
# Adicionando todos os possíveis caminhos ao PATH
ENV PATH="/opt/bitnami/python/bin:/opt/bitnami/mlflow/bin:/usr/local/bin:/.local/bin:${PATH}"
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Criando um link simbólico para garantir que 'python' esteja disponível
RUN ln -sf $(which python3) /usr/local/bin/python || echo "Não foi possível criar o link simbólico"

# Verificando os caminhos
RUN echo "Verificando PATH: $PATH"
RUN find / -name python3 -type f 2>/dev/null || echo "Python3 não encontrado"
RUN find / -name python -type f 2>/dev/null || echo "Python não encontrado"
RUN find / -name mlflow -type f 2>/dev/null || echo "MLflow não encontrado"

USER 1001
