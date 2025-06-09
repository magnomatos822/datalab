#!/bin/bash

# ====================================
# DataLab - Exemplo de Uso Completo
# ====================================
# Este script demonstra como usar o ambiente DataLab

set -e

echo "🚀 DataLab - Exemplo de Uso Completo"
echo "===================================="
echo

# Verificar se o ambiente está rodando
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️  Ambiente não está rodando. Iniciando..."
    ./manage.sh start
    echo "⏳ Aguardando serviços iniciarem..."
    sleep 30
fi

echo "✅ Verificando saúde dos serviços..."
./manage.sh health
echo

echo "🌐 URLs de Acesso:"
./manage.sh urls
echo

echo "📊 Exemplos de Uso:"
echo

echo "1. 💾 Testando MinIO (S3 Storage)"
echo "   - Acesse: http://localhost:9001"
echo "   - Login: admin / admin123"
echo "   - Verifique os buckets: bronze, silver, gold, mlflow, etc."
echo

echo "2. ⚡ Testando Spark"
echo "   - Acesse: http://localhost:8080"
echo "   - Verifique os workers conectados"
echo "   - Submeta um job de exemplo:"
cat << 'EOF'
   
   # Exemplo de job Spark via docker
   docker-compose exec spark-master spark-submit \
     --class org.apache.spark.examples.SparkPi \
     /opt/spark/examples/jars/spark-examples*.jar 10
EOF
echo

echo "3. 🤖 Testando MLflow"
echo "   - Acesse: http://localhost:5000"
echo "   - Crie um experimento de exemplo"
echo "   - Exemplo de código Python:"
cat << 'EOF'
   
   import mlflow
   import mlflow.sklearn
   from sklearn.linear_model import LinearRegression
   from sklearn.datasets import make_regression
   
   # Configurar MLflow
   mlflow.set_tracking_uri("http://localhost:5000")
   
   # Criar dados de exemplo
   X, y = make_regression(n_samples=100, n_features=1, noise=10)
   
   # Treinar modelo
   with mlflow.start_run():
       model = LinearRegression()
       model.fit(X, y)
       
       # Log do modelo
       mlflow.sklearn.log_model(model, "model")
       mlflow.log_metric("r2_score", model.score(X, y))
EOF
echo

echo "4. 🔀 Testando Prefect"
echo "   - Acesse: http://localhost:4200"
echo "   - Crie um flow de exemplo:"
cat << 'EOF'
   
   from prefect import flow, task
   import requests
   
   @task
   def extract_data():
       # Simular extração de dados
       return {"data": [1, 2, 3, 4, 5]}
   
   @task  
   def transform_data(data):
       # Simular transformação
       return {"transformed": [x * 2 for x in data["data"]]}
   
   @task
   def load_data(data):
       # Simular carregamento
       print(f"Loading: {data}")
       return True
   
   @flow
   def etl_flow():
       raw_data = extract_data()
       clean_data = transform_data(raw_data)
       load_data(clean_data)
   
   if __name__ == "__main__":
       etl_flow()
EOF
echo

echo "5. 📓 Testando Jupyter"
echo "   - Acesse: http://localhost:8888"
echo "   - Use os notebooks em /notebooks"
echo "   - Exemplo de conexão com MinIO:"
cat << 'EOF'
   
   import boto3
   
   # Configurar cliente S3 (MinIO)
   s3_client = boto3.client(
       's3',
       endpoint_url='http://minio:9000',
       aws_access_key_id='minioadmin',
       aws_secret_access_key='minioadmin'
   )
   
   # Listar buckets
   buckets = s3_client.list_buckets()
   print([bucket['Name'] for bucket in buckets['Buckets']])
EOF
echo

echo "6. 🖥️  Testando Streamlit"
echo "   - Acesse: http://localhost:8501"
echo "   - Exemplo de app:"
cat << 'EOF'
   
   import streamlit as st
   import pandas as pd
   import mlflow
   
   st.title("DataLab - Dashboard de Exemplo")
   
   # Conectar com MLflow
   mlflow.set_tracking_uri("http://mlflow:5000")
   
   # Mostrar experimentos
   experiments = mlflow.search_experiments()
   st.write("Experimentos MLflow:", experiments)
   
   # Gráfico de exemplo
   data = pd.DataFrame({
       'x': range(10),
       'y': [x**2 for x in range(10)]
   })
   st.line_chart(data.set_index('x'))
EOF
echo

echo "7. 📈 Testando Monitoramento"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana: http://localhost:3000 (admin/admin)"
echo "   - Métricas dos serviços disponíveis"
echo

echo "📝 Comandos Úteis:"
echo
echo "# Ver logs em tempo real"
echo "./manage.sh logs"
echo
echo "# Verificar status"
echo "./manage.sh status"
echo
echo "# Parar ambiente"
echo "./manage.sh stop"
echo
echo "# Reiniciar ambiente"
echo "./manage.sh restart"
echo
echo "# Limpeza completa"
echo "./manage.sh clean"
echo

echo "🎯 Próximos Passos:"
echo "1. Explore cada serviço através das URLs fornecidas"
echo "2. Execute os exemplos de código fornecidos"
echo "3. Crie seus próprios notebooks e workflows"
echo "4. Configure dashboards no Grafana"
echo "5. Implemente pipelines de dados completos"
echo

echo "📚 Documentação:"
echo "- README principal: README.md"
echo "- Documentação dos serviços: docs/"
echo "- Exemplos de código: app/"
echo "- Notebooks: notebooks/"
echo

echo "✨ Ambiente DataLab pronto para uso!"
