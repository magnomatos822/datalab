#!/bin/bash

# Script para configurar o banco de dados no PostgreSQL 17 externo para o Airflow
# Este script deve ser executado no servidor onde o PostgreSQL 17 está instalado
# ou em uma máquina com acesso ao servidor PostgreSQL

set -e

echo "=== Configurando banco de dados no PostgreSQL 17 para Airflow ==="

# Configurações de conexão - modifique conforme necessário
PG_HOST="10.10.120.125"  # Use o endereço correto do seu servidor PostgreSQL
PG_PORT="5000"
PG_ADMIN_USER="postgres"  # Usuário administrador do PostgreSQL
PG_ADMIN_PASSWORD="postgres"  # Senha do usuário administrador

# Função para executar comandos SQL
run_psql() {
  PGPASSWORD="$PG_ADMIN_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN_USER" -c "$1"
}

# Configuração para o Airflow
echo "Configurando banco de dados para o Airflow..."

# Verificar se usuário airflow existe
USER_EXISTS=$(PGPASSWORD="$PG_ADMIN_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN_USER" -tAc "SELECT 1 FROM pg_roles WHERE rolname='airflow'")

if [ "$USER_EXISTS" != "1" ]; then
  echo "Criando usuário 'airflow'..."
  run_psql "CREATE USER airflow WITH PASSWORD 'airflow';"
else
  echo "Usuário 'airflow' já existe."
fi

# Verificar se o banco de dados airflow existe
DB_EXISTS=$(PGPASSWORD="$PG_ADMIN_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='airflow'")

if [ "$DB_EXISTS" != "1" ]; then
  echo "Criando banco de dados 'airflow'..."
  run_psql "CREATE DATABASE airflow;"
  run_psql "GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;"
  run_psql "ALTER DATABASE airflow OWNER TO airflow;"
  
  # Configurar extensões necessárias para o Airflow
  PGPASSWORD="$PG_ADMIN_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN_USER" -d airflow -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
else
  echo "Banco de dados 'airflow' já existe."
fi

echo "=== Configuração do banco de dados concluída! ==="
echo "O seguinte banco de dados foi configurado:"
echo "- airflow (para o Apache Airflow)"
echo ""
echo "Agora você precisa:"
echo "1. Ajustar os IPs no arquivo docker-compose.yml para apontar para o seu servidor PostgreSQL"
echo "2. Garantir que o PostgreSQL esteja configurado para aceitar conexões remotas"
echo "3. Verificar se o pg_hba.conf permite conexões dos hosts dos containers"
echo "4. Iniciar os serviços com o comando:"
echo "   docker-compose up -d airflow-webserver airflow-scheduler"