#!/bin/bash

# Script para inicializar diretórios do Airflow e corrigir permissões
# Este script deve ser executado no host antes de iniciar os contêineres

set -e

echo "=== Inicializando diretórios do Airflow e corrigindo permissões ==="

# Diretório base do projeto
BASE_DIR=$(dirname $(dirname $(readlink -f $0)))
AIRFLOW_DIR="$BASE_DIR/data/airflow"

# Criar diretórios necessários para o Airflow
echo "Criando diretórios para o Airflow..."
mkdir -p "$AIRFLOW_DIR/logs"
mkdir -p "$AIRFLOW_DIR/logs/scheduler"
mkdir -p "$AIRFLOW_DIR/logs/webserver"
mkdir -p "$AIRFLOW_DIR/logs/worker"
mkdir -p "$AIRFLOW_DIR/dags"
mkdir -p "$AIRFLOW_DIR/plugins"
mkdir -p "$AIRFLOW_DIR/config"

# Definir permissões (50000 é o AIRFLOW_UID no docker-compose.yml)
echo "Definindo permissões dos diretórios..."
# Definir permissões apenas para os diretórios recém-criados
chmod -R 777 "$AIRFLOW_DIR/logs"
chmod -R 777 "$AIRFLOW_DIR/dags"
chmod -R 777 "$AIRFLOW_DIR/plugins"
chmod -R 777 "$AIRFLOW_DIR/config"

echo "=== Inicialização de diretórios concluída! ==="
echo "Agora você pode iniciar os contêineres do Airflow com:"
echo "docker-compose up -d airflow-webserver airflow-scheduler"