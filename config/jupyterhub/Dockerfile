FROM jupyterhub/jupyterhub:4.0.2

USER root
RUN pip install pyspark==3.5.5 boto3 pandas matplotlib seaborn scikit-learn mlflow prefect

# Configuração para conectar ao Spark
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Adiciona o diretório /.local/bin ao PATH
ENV PATH="/.local/bin:${PATH}"

# Criar usuário jovyan que é usado normalmente em imagens Jupyter
RUN useradd -m -s /bin/bash -N jovyan
USER jovyan
