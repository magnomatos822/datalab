#!/bin/bash
set -e

# Função para gerenciar permissões - com abordagem mais suave
function setup_permissions() {
  echo "Verificando permissões para os diretórios do Airflow..."
  
  # Ajustar permissões diretamente - ignorando erros para volumes montados
  for dir in "logs" "dags" "plugins" "config"; do
    echo "Verificando permissões para ${AIRFLOW_HOME}/${dir}"
    chmod -R 777 "${AIRFLOW_HOME}/${dir}" 2>/dev/null || echo "Aviso: Não foi possível alterar permissões de ${AIRFLOW_HOME}/${dir} (volume montado)"
  done
  
  # Garantir que temos o arquivo .airflowignore para evitar erros de leitura
  touch ${AIRFLOW_HOME}/dags/.airflowignore 2>/dev/null || echo "Aviso: Não foi possível criar .airflowignore"
  
  echo "Verificação de permissões concluída."
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

# Executar apenas verificação de permissões (sem tentar chown)
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
  airflow db migrate && \
  # Criar usuário admin se não existir
  (airflow users list | grep -q admin || \
    airflow users create \
      --username admin \
      --firstname Admin \
      --lastname Admin \
      --role Admin \
      --email admin@example.com \
      --password admin) && \
  airflow connections create-default-connections
  exec airflow webserver
elif [[ "$1" == "scheduler" ]]; then
  echo "Iniciando Airflow Scheduler..."
  exec airflow scheduler
elif [[ "$1" == "init" ]]; then
  echo "Inicializando banco de dados do Airflow..."
  airflow db migrate && \
  airflow users create \
    --username admin \
    --firstname Admin \
    --lastname Admin \
    --role Admin \
    --email admin@example.com \
    --password admin && \
  airflow connections create-default-connections
  
  exit 0
else
  exec "$@"
fi