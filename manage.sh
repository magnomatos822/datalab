#!/bin/bash

# ====================================
# DataLab - Script de Gerenciamento
# ====================================
# Este script facilita o gerenciamento do ambiente DataLab

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para exibir ajuda
show_help() {
    echo -e "${BLUE}DataLab - Script de Gerenciamento${NC}"
    echo
    echo "Uso: $0 [COMANDO] [OPÇÕES]"
    echo
    echo "COMANDOS:"
    echo "  start [perfil]     - Inicia todo o ambiente ou um perfil específico"
    echo "  stop [perfil]      - Para todo o ambiente ou um perfil específico"
    echo "  restart [perfil]   - Reinicia todo o ambiente ou um perfil específico"
    echo "  status             - Mostra o status dos serviços"
    echo "  logs [serviço]     - Mostra logs de todos os serviços ou de um específico"
    echo "  clean              - Remove todos os containers e volumes"
    echo "  build              - Reconstrói as imagens customizadas"
    echo "  health             - Verifica a saúde dos serviços"
    echo "  urls               - Mostra as URLs de acesso dos serviços"
    echo "  credentials        - Mostra todas as credenciais de acesso"
    echo
    echo "PERFIS DISPONÍVEIS:"
    echo "  core              - Serviços essenciais (MinIO, Kafka)"
    echo "  processing        - Processamento (Spark)"
    echo "  ml                - Machine Learning (MLflow, Prefect)"
    echo "  visualization     - Visualização (Jupyter, Streamlit)"
    echo "  monitoring        - Monitoramento (Prometheus, Grafana)"
    echo "  all               - Todos os serviços (padrão)"
    echo
    echo "EXEMPLOS:"
    echo "  $0 start                    # Inicia todos os serviços"
    echo "  $0 start core              # Inicia apenas serviços essenciais"
    echo "  $0 stop                    # Para todos os serviços"
    echo "  $0 logs mlflow             # Mostra logs do MLflow"
    echo "  $0 health                  # Verifica saúde dos serviços"
    echo "  $0 credentials             # Mostra todas as credenciais"
}

# Função para verificar se o Docker está rodando
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}Erro: Docker não está rodando!${NC}"
        exit 1
    fi
}

# Função para verificar se docker-compose está instalado
check_compose() {
    if ! command -v docker-compose >/dev/null 2>&1; then
        echo -e "${RED}Erro: docker-compose não está instalado!${NC}"
        exit 1
    fi
}

# Função para obter serviços por perfil
get_services_by_profile() {
    local profile=$1
    case $profile in
        "core")
            echo "minio kafka"
            ;;
        "processing")
            echo "spark-master spark-worker"
            ;;
        "ml")
            echo "mlflow prefect"
            ;;
        "visualization")
            echo "jupyter streamlit"
            ;;
        "monitoring")
            echo "prometheus grafana"
            ;;
        "all"|"")
            echo ""  # Todos os serviços
            ;;
        *)
            echo -e "${RED}Perfil inválido: $profile${NC}"
            echo "Use: core, processing, ml, visualization, monitoring, ou all"
            exit 1
            ;;
    esac
}

# Função para iniciar serviços
start_services() {
    local profile=${1:-all}
    local services=$(get_services_by_profile $profile)
    
    echo -e "${GREEN}Iniciando ambiente DataLab...${NC}"
    
    if [ "$profile" = "all" ] || [ -z "$services" ]; then
        echo -e "${BLUE}Iniciando todos os serviços...${NC}"
        docker-compose up -d
    else
        echo -e "${BLUE}Iniciando serviços do perfil '$profile': $services${NC}"
        docker-compose up -d $services
    fi
    
    echo -e "${GREEN}Ambiente iniciado com sucesso!${NC}"
    show_urls
}

# Função para parar serviços
stop_services() {
    local profile=${1:-all}
    local services=$(get_services_by_profile $profile)
    
    echo -e "${YELLOW}Parando ambiente DataLab...${NC}"
    
    if [ "$profile" = "all" ] || [ -z "$services" ]; then
        echo -e "${BLUE}Parando todos os serviços...${NC}"
        docker-compose down
    else
        echo -e "${BLUE}Parando serviços do perfil '$profile': $services${NC}"
        docker-compose stop $services
    fi
    
    echo -e "${GREEN}Serviços parados com sucesso!${NC}"
}

# Função para reiniciar serviços
restart_services() {
    local profile=${1:-all}
    stop_services $profile
    sleep 2
    start_services $profile
}

# Função para mostrar status
show_status() {
    echo -e "${BLUE}Status dos serviços DataLab:${NC}"
    docker-compose ps
}

# Função para mostrar logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        echo -e "${BLUE}Mostrando logs de todos os serviços...${NC}"
        docker-compose logs -f
    else
        echo -e "${BLUE}Mostrando logs do serviço: $service${NC}"
        docker-compose logs -f $service
    fi
}

# Função para limpeza completa
clean_environment() {
    echo -e "${YELLOW}Atenção: Esta operação irá remover todos os containers e volumes!${NC}"
    read -p "Tem certeza? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Removendo ambiente DataLab...${NC}"
        docker-compose down -v --remove-orphans
        docker system prune -f
        echo -e "${GREEN}Ambiente limpo com sucesso!${NC}"
    else
        echo -e "${BLUE}Operação cancelada.${NC}"
    fi
}

# Função para build das imagens
build_images() {
    echo -e "${BLUE}Reconstruindo imagens customizadas...${NC}"
    docker-compose build --no-cache
    echo -e "${GREEN}Imagens reconstruídas com sucesso!${NC}"
}

# Função para verificar saúde dos serviços
check_health() {
    echo -e "${BLUE}Verificando saúde dos serviços...${NC}"
    
    # Lista de serviços e suas portas para verificação
    declare -A services_health=(
        ["minio"]="9000"
        ["kafka"]="9092"
        ["spark-master"]="8080"
        ["mlflow"]="5000"
        ["prefect"]="4200"
        ["jupyter"]="8888"
        ["streamlit"]="8501"
        ["prometheus"]="9090"
        ["grafana"]="3000"
    )
    
    for service in "${!services_health[@]}"; do
        port=${services_health[$service]}
        if docker-compose ps $service | grep -q "Up"; then
            if curl -s -f "http://localhost:$port" >/dev/null 2>&1; then
                echo -e "${GREEN}✓${NC} $service (porta $port) - ${GREEN}Saudável${NC}"
            else
                echo -e "${YELLOW}⚠${NC} $service (porta $port) - ${YELLOW}Rodando mas não responsivo${NC}"
            fi
        else
            echo -e "${RED}✗${NC} $service - ${RED}Não está rodando${NC}"
        fi
    done
}

# Função para mostrar URLs de acesso
show_urls() {
    echo
    echo -e "${BLUE}URLs de Acesso dos Serviços:${NC}"
    echo -e "${GREEN}MinIO (Storage):${NC}        http://localhost:9001"
    echo -e "${GREEN}Spark Master:${NC}           http://localhost:8080"
    echo -e "${GREEN}MLflow:${NC}                 http://localhost:5000"
    echo -e "${GREEN}Prefect:${NC}                http://localhost:4200"
    echo -e "${GREEN}JupyterHub:${NC}             http://localhost:8888"
    echo -e "${GREEN}Streamlit:${NC}              http://localhost:8501"
    echo -e "${GREEN}Prometheus:${NC}             http://localhost:9090"
    echo -e "${GREEN}Grafana:${NC}                http://localhost:3000"
    echo -e "${GREEN}Airflow:${NC}                http://localhost:8082 (quando ativo)"
    echo
    show_credentials
}

# Função para mostrar todas as credenciais
show_credentials() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                    CREDENCIAIS DE ACESSO - DATALAB${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo
    
    echo -e "${GREEN}🗄️  MinIO (Object Storage)${NC}"
    echo -e "   ${YELLOW}URL:${NC}      http://localhost:9001"
    echo -e "   ${YELLOW}Usuário:${NC}  admin"
    echo -e "   ${YELLOW}Senha:${NC}    admin123"
    echo -e "   ${YELLOW}Padrão:${NC}   minioadmin / minioadmin (fallback)"
    echo
    
    echo -e "${GREEN}📊 Grafana (Dashboards)${NC}"
    echo -e "   ${YELLOW}URL:${NC}      http://localhost:3000"
    echo -e "   ${YELLOW}Usuário:${NC}  admin"
    echo -e "   ${YELLOW}Senha:${NC}    admin123 (docker-compose.yml) ou admin (monitoring.yml)"
    echo
    
    echo -e "${GREEN}📓 JupyterHub (Notebooks)${NC}"
    echo -e "   ${YELLOW}URL:${NC}      http://localhost:8888"
    echo -e "   ${YELLOW}Usuários permitidos:${NC}"
    echo -e "     - magnomatos822 / datalab"
    echo -e "     - admin / datalab (administrador)"
    echo
    
    echo -e "${GREEN}🌊 Airflow (Orquestração)${NC}"
    echo -e "   ${YELLOW}URL:${NC}      http://localhost:8082 (quando ativo)"
    echo -e "   ${YELLOW}Usuário:${NC}  admin"
    echo -e "   ${YELLOW}Senha:${NC}    admin"
    echo -e "   ${YELLOW}Email:${NC}    admin@example.com"
    echo
    
    echo -e "${GREEN}🚀 MLflow (ML Lifecycle)${NC}"
    echo -e "   ${YELLOW}URL:${NC}      http://localhost:5000"
    echo -e "   ${YELLOW}Acesso:${NC}   Sem autenticação (público)"
    echo -e "   ${YELLOW}Storage:${NC}  Integrado com MinIO"
    echo
    
    echo -e "${GREEN}⚡ Prefect (Workflow Orchestration)${NC}"
    echo -e "   ${YELLOW}URL:${NC}      http://localhost:4200"
    echo -e "   ${YELLOW}Acesso:${NC}   Sem autenticação (público)"
    echo -e "   ${YELLOW}Storage:${NC}  Integrado com MinIO"
    echo
    
    echo -e "${GREEN}🌐 Streamlit (Web Apps)${NC}"
    echo -e "   ${YELLOW}URL:${NC}      http://localhost:8501"
    echo -e "   ${YELLOW}Acesso:${NC}   Sem autenticação (público)"
    echo
    
    echo -e "${GREEN}🔥 Apache Spark${NC}"
    echo -e "   ${YELLOW}Master UI:${NC} http://localhost:8080"
    echo -e "   ${YELLOW}Acesso:${NC}    Sem autenticação (público)"
    echo -e "   ${YELLOW}Workers:${NC}   2 workers configurados"
    echo
    
    echo -e "${GREEN}📈 Prometheus (Metrics)${NC}"
    echo -e "   ${YELLOW}URL:${NC}      http://localhost:9090"
    echo -e "   ${YELLOW}Acesso:${NC}   Sem autenticação (público)"
    echo
    
    echo -e "${GREEN}📡 Kafka (Event Streaming)${NC}"
    echo -e "   ${YELLOW}Broker:${NC}   localhost:9092"
    echo -e "   ${YELLOW}External:${NC} localhost:29092"
    echo -e "   ${YELLOW}Acesso:${NC}   Sem autenticação (PLAINTEXT)"
    echo
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                        VARIÁVEIS DE AMBIENTE${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo
    
    echo -e "${GREEN}🔐 Credenciais S3/MinIO para aplicações:${NC}"
    echo -e "   ${YELLOW}AWS_ACCESS_KEY_ID:${NC}     minioadmin (ou admin)"
    echo -e "   ${YELLOW}AWS_SECRET_ACCESS_KEY:${NC} minioadmin (ou admin123)"
    echo -e "   ${YELLOW}S3_ENDPOINT:${NC}           http://minio:9000 (interno)"
    echo -e "   ${YELLOW}S3_ENDPOINT:${NC}           http://localhost:9000 (externo)"
    echo
    
    echo -e "${GREEN}🗃️  PostgreSQL (quando utilizado):${NC}"
    echo -e "   ${YELLOW}Host:${NC}     10.10.120.125"
    echo -e "   ${YELLOW}Port:${NC}     5000"
    echo -e "   ${YELLOW}Usuário:${NC}  postgres"
    echo -e "   ${YELLOW}Senha:${NC}    postgres"
    echo -e "   ${YELLOW}DBs:${NC}      mlflow, airflow"
    echo
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}💡 Dicas de Segurança:${NC}"
    echo -e "   • Estas são credenciais de desenvolvimento"
    echo -e "   • Para produção, altere todas as senhas padrão"
    echo -e "   • Configure autenticação adequada para cada serviço"
    echo -e "   • Use variáveis de ambiente para credenciais sensíveis"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo
}

# Função principal
main() {
    check_docker
    check_compose
    
    case ${1:-help} in
        "start")
            start_services $2
            ;;
        "stop")
            stop_services $2
            ;;
        "restart")
            restart_services $2
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs $2
            ;;
        "clean")
            clean_environment
            ;;
        "build")
            build_images
            ;;
        "health")
            check_health
            ;;
        "urls")
            show_urls
            ;;
        "credentials")
            show_credentials
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}Comando inválido: $1${NC}"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Executa a função principal com todos os argumentos
main "$@"
