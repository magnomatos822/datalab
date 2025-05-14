#!/bin/bash
set -e

# Função para gerenciar permissões
function setup_permissions() {
  echo "Configurando permissões para o usuário airflow..."
  mkdir -p ${AIRFLOW_HOME}/logs ${AIRFLOW_HOME}/dags ${AIRFLOW_HOME}/plugins
  chown -R ${AIRFLOW_USER}:${AIRFLOW_USER} ${AIRFLOW_HOME}
}

# Inicialização específica para diferentes componentes
function wait_for_postgres() {
  local postgres_host="${1:-postgres}"
  local postgres_port="${2:-5432}"
  local max_retries=${3:-30}
  local retry=0
  
  echo "Verificando disponibilidade do PostgreSQL em ${postgres_host}:${postgres_port}..."

  while ! nc -z "${postgres_host}" "${postgres_port}" > /dev/null 2>&1; do
    retry=$(( retry + 1 ))
    if [[ ${retry} -ge ${max_retries} ]]; then
      echo "Erro: falha ao se conectar ao PostgreSQL após ${max_retries} tentativas."
      exit 1
    fi
    echo "PostgreSQL não disponível ainda, tentando novamente em 5 segundos..."
    sleep 5
  done
  
  echo "Conexão com PostgreSQL estabelecida com sucesso!"
}

setup_permissions

# Conectado com ambientes externos se necessário
if [[ -n "${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN}" ]]; then
  DB_HOST=$(echo ${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN} | cut -d'@' -f2 | cut -d'/' -f1 | cut -d':' -f1)
  DB_PORT=$(echo ${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN} | cut -d'@' -f2 | cut -d'/' -f1 | cut -d':' -f2)

  # Se temos uma conexão com PostgreSQL, espere por ele
  if [[ ${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN} == postgresql* ]]; then
    wait_for_postgres "${DB_HOST}" "${DB_PORT}"
  fi
fi

# Executa comandos como usuário airflow
if [[ "$1" == "webserver" ]]; then
  echo "Iniciando Airflow Webserver..."
  gosu ${AIRFLOW_USER} airflow db init
  gosu ${AIRFLOW_USER} airflow db upgrade
  
  # Criar usuário admin se não existir
  if ! gosu ${AIRFLOW_USER} airflow users list | grep -q admin; then
    gosu ${AIRFLOW_USER} airflow users create \
      --username admin \
      --firstname Admin \
      --lastname Admin \
      --role Admin \
      --email admin@example.com \
      --password admin
  fi
  
  exec gosu ${AIRFLOW_USER} airflow webserver
elif [[ "$1" == "scheduler" ]]; then
  echo "Iniciando Airflow Scheduler..."
  exec gosu ${AIRFLOW_USER} airflow scheduler
elif [[ "$1" == "init" ]]; then
  echo "Inicializando banco de dados do Airflow..."
  gosu ${AIRFLOW_USER} airflow db init
  
  gosu ${AIRFLOW_USER} airflow users create \
    --username admin \
    --firstname Admin \
    --lastname Admin \
    --role Admin \
    --email admin@example.com \
    --password admin
  
  exit 0
else
  exec gosu ${AIRFLOW_USER} "$@"
fi