#!/bin/bash

# Define cores para saída
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretório de configuração para garantir que os serviços possam ser iniciados
mkdir -p config/prometheus
mkdir -p config/grafana/provisioning

# Cria arquivo prometheus.yml básico se não existir
if [ ! -f config/prometheus/prometheus.yml ]; then
  echo "Criando arquivo de configuração básica para o Prometheus..."
  cat > config/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'consul'
    consul_sd_configs:
      - server: 'consul:8500'
    relabel_configs:
      - source_labels: ['__meta_consul_service']
        target_label: 'service'
EOF
fi

# Função para exibir ajuda
show_help() {
    echo -e "${BLUE}== Script de Ambiente DataLab ==${NC}"
    echo -e "Uso: $0 [opções]"
    echo ""
    echo -e "Opções:"
    echo -e "  ${GREEN}start${NC} [ambiente]      - Inicia um ambiente específico ou todos se não especificado"
    echo -e "  ${YELLOW}stop${NC} [ambiente]       - Para um ambiente específico ou todos se não especificado"
    echo -e "  ${BLUE}status${NC}               - Mostra status dos contêineres em execução"
    echo -e "  ${RED}clean${NC}                - Remove todos os contêineres parados e redes não utilizadas"
    echo ""
    echo -e "Ambientes disponíveis:"
    echo -e "  ${GREEN}core${NC}          - Serviços de infraestrutura core (MinIO, Kafka, Consul)"
    echo -e "  ${GREEN}processing${NC}    - Serviços de processamento de dados (Spark, NiFi)"
    echo -e "  ${GREEN}ml${NC}            - Serviços de machine learning (MLflow, Prefect, Airflow)"
    echo -e "  ${GREEN}visualization${NC} - Serviços de visualização (JupyterHub, Streamlit)"
    echo -e "  ${GREEN}monitoring${NC}    - Serviços de monitoramento (Prometheus, Grafana)"
    echo -e "  ${GREEN}all${NC}           - Todos os serviços"
    echo ""
    echo -e "Exemplos:"
    echo -e "  $0 start core"
    echo -e "  $0 start core processing"
    echo -e "  $0 start all"
    echo -e "  $0 stop ml"
}

# Verifica se a rede Docker existe, caso contrário, cria
check_network() {
    if ! docker network ls | grep -q dataflow-network; then
        echo -e "${BLUE}Criando rede dataflow-network...${NC}"
        docker network create dataflow-network
    fi
}

# Função para preparar volumes com permissões adequadas
prepare_volumes() {
    echo -e "${BLUE}Verificando e preparando volumes...${NC}"
    
    # Garantir que os diretórios de dados existem e têm permissões corretas
    mkdir -p data/minio
    mkdir -p data/consul
    chmod -R 777 data/minio
    chmod -R 777 data/consul
    
    # Remover volumes antigos que podem ter permissões incorretas
    if docker volume ls | grep -q minio-data; then
        echo -e "${YELLOW}Removendo volume antigo do MinIO...${NC}"
        docker volume rm minio-data || true
    fi
    
    if docker volume ls | grep -q consul-data; then
        echo -e "${YELLOW}Removendo volume antigo do Consul...${NC}"
        docker volume rm consul-data || true
    fi
    
    # Criar novos volumes com permissões adequadas
    echo -e "${BLUE}Criando volumes com permissões corretas...${NC}"
    docker volume create --name minio-data
    docker volume create --name consul-data
    
    # Inicializar volumes com permissões corretas usando contêineres temporários
    echo -e "${BLUE}Inicializando volume MinIO com permissões corretas...${NC}"
    docker run --rm -v minio-data:/data busybox sh -c "chown -R 1001:1001 /data && chmod -R 777 /data"
    
    echo -e "${BLUE}Inicializando volume Consul com permissões corretas...${NC}"
    docker run --rm -v consul-data:/data busybox sh -c "chown -R 1001:1001 /data && chmod -R 777 /data"
}

# Função para iniciar um ambiente específico
start_environment() {
    local env=$1
    check_network
    prepare_volumes
    
    case $env in
        core)
            echo -e "${GREEN}Iniciando ambiente CORE...${NC}"
            # Modifique o arquivo docker-compose.core.yml temporariamente para adicionar a flag --ignore-formatted ao Kafka
            if grep -q "CLUSTER_ID" docker-compose.core.yml && grep -q "kafka-storage.sh format" docker-compose.core.yml; then
                echo -e "${BLUE}Adicionando flag --ignore-formatted para o Kafka...${NC}"
                sed -i 's/kafka-storage.sh format -t/kafka-storage.sh format --ignore-formatted -t/g' docker-compose.core.yml
                docker compose -f docker-compose.core.yml up -d
                # Restaure o arquivo original após a inicialização
                sed -i 's/kafka-storage.sh format --ignore-formatted -t/kafka-storage.sh format -t/g' docker-compose.core.yml
            else
                docker compose -f docker-compose.core.yml up -d
            fi
            ;;
        processing)
            echo -e "${GREEN}Iniciando ambiente PROCESSING...${NC}"
            docker compose -f docker-compose.processing.yml up -d
            ;;
        ml)
            echo -e "${GREEN}Iniciando ambiente ML...${NC}"
            docker compose -f docker-compose.ml.yml up -d
            ;;
        visualization)
            echo -e "${GREEN}Iniciando ambiente VISUALIZATION...${NC}"
            docker compose -f docker-compose.visualization.yml up -d
            ;;
        monitoring)
            echo -e "${GREEN}Iniciando ambiente MONITORING...${NC}"
            docker compose -f docker-compose.monitoring.yml up -d
            ;;
        all)
            echo -e "${GREEN}Iniciando TODOS os ambientes...${NC}"
            # Modifique o arquivo docker-compose.core.yml temporariamente para adicionar a flag --ignore-formatted ao Kafka
            if grep -q "CLUSTER_ID" docker-compose.core.yml && grep -q "kafka-storage.sh format" docker-compose.core.yml; then
                echo -e "${BLUE}Adicionando flag --ignore-formatted para o Kafka...${NC}"
                sed -i 's/kafka-storage.sh format -t/kafka-storage.sh format --ignore-formatted -t/g' docker-compose.core.yml
                docker compose -f docker-compose.core.yml -f docker-compose.processing.yml -f docker-compose.ml.yml -f docker-compose.visualization.yml -f docker-compose.monitoring.yml up -d
                # Restaure o arquivo original após a inicialização
                sed -i 's/kafka-storage.sh format --ignore-formatted -t/kafka-storage.sh format -t/g' docker-compose.core.yml
            else
                docker compose -f docker-compose.core.yml -f docker-compose.processing.yml -f docker-compose.ml.yml -f docker-compose.visualization.yml -f docker-compose.monitoring.yml up -d
            fi
            ;;
        *)
            echo -e "${RED}Ambiente '$env' não reconhecido. Use 'core', 'processing', 'ml', 'visualization', 'monitoring' ou 'all'.${NC}"
            exit 1
            ;;
    esac
}

# Função para parar um ambiente específico
stop_environment() {
    local env=$1
    
    case $env in
        core)
            echo -e "${YELLOW}Parando ambiente CORE...${NC}"
            docker compose -f docker-compose.core.yml down
            ;;
        processing)
            echo -e "${YELLOW}Parando ambiente PROCESSING...${NC}"
            docker compose -f docker-compose.processing.yml down
            ;;
        ml)
            echo -e "${YELLOW}Parando ambiente ML...${NC}"
            docker compose -f docker-compose.ml.yml down
            ;;
        visualization)
            echo -e "${YELLOW}Parando ambiente VISUALIZATION...${NC}"
            docker compose -f docker-compose.visualization.yml down
            ;;
        monitoring)
            echo -e "${YELLOW}Parando ambiente MONITORING...${NC}"
            docker compose -f docker-compose.monitoring.yml down
            ;;
        all)
            echo -e "${YELLOW}Parando TODOS os ambientes...${NC}"
            docker compose -f docker-compose.core.yml -f docker-compose.processing.yml -f docker-compose.ml.yml -f docker-compose.visualization.yml -f docker-compose.monitoring.yml down
            ;;
        *)
            echo -e "${RED}Ambiente '$env' não reconhecido. Use 'core', 'processing', 'ml', 'visualization', 'monitoring' ou 'all'.${NC}"
            exit 1
            ;;
    esac
}

# Principal
if [ $# -lt 1 ]; then
    show_help
    exit 0
fi

command=$1
shift

case $command in
    start)
        if [ $# -eq 0 ]; then
            start_environment all
        else
            for env in "$@"; do
                start_environment "$env"
            done
        fi
        ;;
    stop)
        if [ $# -eq 0 ]; then
            stop_environment all
        else
            for env in "$@"; do
                stop_environment "$env"
            done
        fi
        ;;
    status)
        echo -e "${BLUE}Status dos contêineres:${NC}"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        ;;
    clean)
        echo -e "${RED}Removendo contêineres parados...${NC}"
        docker container prune -f
        echo -e "${RED}Removendo redes não utilizadas...${NC}"
        docker network prune -f
        ;;
    *)
        show_help
        exit 1
        ;;
esac

exit 0
