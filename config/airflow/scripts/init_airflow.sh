#!/bin/bash
# Script para inicializar o Airflow com configurações padrão e DAGs de exemplo

set -e

echo "Inicializando configurações do Apache Airflow..."

# Verificar se as pastas necessárias existem
if [ ! -d "${AIRFLOW_HOME}/dags" ]; then
  echo "Criando pasta de DAGs..."
  mkdir -p "${AIRFLOW_HOME}/dags"
fi

if [ ! -d "${AIRFLOW_HOME}/logs" ]; then
  echo "Criando pasta de logs..."
  mkdir -p "${AIRFLOW_HOME}/logs"
fi

if [ ! -d "${AIRFLOW_HOME}/plugins" ]; then
  echo "Criando pasta de plugins..."
  mkdir -p "${AIRFLOW_HOME}/plugins"
fi

# Criar DAG de exemplo se não existir
if [ ! -f "${AIRFLOW_HOME}/dags/example_medallion.py" ]; then
  echo "Criando DAG de exemplo para arquitetura medallion..."
  cat > "${AIRFLOW_HOME}/dags/example_medallion.py" << 'EOL'
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

default_args = {
    'owner': 'datalab',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'medallion_architecture_example',
    default_args=default_args,
    description='Um exemplo de DAG implementando a arquitetura Medallion',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 5, 15),
    catchup=False,
    tags=['exemplo', 'medallion', 'datalab'],
) as dag:

    # Bronze layer - Ingestão de dados brutos
    ingest_to_bronze = SparkSubmitOperator(
        task_id='ingest_to_bronze',
        conn_id='spark_default',
        application='/opt/spark-apps/medallion_example.py',
        application_args=['--layer', 'bronze'],
        name='bronze_ingest_job',
        conf={
            'spark.driver.memory': '1g',
            'spark.executor.memory': '1g'
        }
    )
    
    # Silver layer - Limpeza e transformação
    process_to_silver = SparkSubmitOperator(
        task_id='process_to_silver',
        conn_id='spark_default',
        application='/opt/spark-apps/medallion_example.py',
        application_args=['--layer', 'silver'],
        name='silver_process_job',
        conf={
            'spark.driver.memory': '1g',
            'spark.executor.memory': '1g'
        }
    )
    
    # Gold layer - Agregações e análises
    transform_to_gold = SparkSubmitOperator(
        task_id='transform_to_gold',
        conn_id='spark_default',
        application='/opt/spark-apps/medallion_example.py',
        application_args=['--layer', 'gold'],
        name='gold_transform_job',
        conf={
            'spark.driver.memory': '1g',
            'spark.executor.memory': '1g'
        }
    )
    
    def send_notification(**kwargs):
        """Enviar notificação após conclusão do pipeline."""
        print("Pipeline Medallion concluído com sucesso!")
        return "Notificação enviada"
        
    notification = PythonOperator(
        task_id='send_notification',
        python_callable=send_notification,
    )
    
    # Definir o fluxo de tarefas
    ingest_to_bronze >> process_to_silver >> transform_to_gold >> notification
EOL
fi

echo "Inicialização do Airflow concluída com sucesso!"