#!/bin/bash

# Script otimizado para build do DataLab
# Inclui estratégias para resolver problemas de timeout

set -e

echo "🚀 DataLab - Build Otimizado"
echo "================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    log_error "Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Função para verificar espaço em disco
check_disk_space() {
    available=$(df / | awk 'NR==2{print $4}')
    required=5000000  # 5GB in KB
    
    if [ "$available" -lt "$required" ]; then
        log_warning "Espaço em disco baixo. Limpando imagens Docker não utilizadas..."
        docker system prune -f
    fi
}

# Função para configurar Docker para builds otimizados
configure_docker_build() {
    log_info "Configurando Docker para builds otimizados..."
    
    # Configurar BuildKit para builds paralelos
    export DOCKER_BUILDKIT=1
    export BUILDKIT_PROGRESS=plain
    
    # Configurar cache do Docker
    docker buildx create --use --name datalab-builder 2>/dev/null || true
}

# Função para build com retry
build_with_retry() {
    local service=$1
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Tentativa $attempt/$max_attempts para build do $service..."
        
        if docker-compose -f docker-compose.simple.yml build --no-cache $service; then
            log_success "Build do $service concluído!"
            return 0
        else
            log_warning "Build do $service falhou na tentativa $attempt"
            if [ $attempt -lt $max_attempts ]; then
                log_info "Aguardando 10 segundos antes da próxima tentativa..."
                sleep 10
            fi
            attempt=$((attempt + 1))
        fi
    done
    
    log_error "Build do $service falhou após $max_attempts tentativas"
    return 1
}

# Função principal
main() {
    log_info "Iniciando build otimizado do DataLab..."
    
    # Verificações iniciais
    check_disk_space
    configure_docker_build
    
    # Parar serviços existentes
    log_info "Parando serviços existentes..."
    docker-compose -f docker-compose.simple.yml down 2>/dev/null || true
    
    # Limpar volumes órfãos
    log_info "Limpando volumes órfãos..."
    docker volume prune -f
    
    # Build dos serviços que precisam ser construídos
    log_info "Construindo serviços customizados..."
    
    # MLflow primeiro (menor e mais simples)
    if build_with_retry "mlflow"; then
        log_success "MLflow construído com sucesso!"
    else
        log_error "Falha no build do MLflow"
        exit 1
    fi
    
    # Puxar imagens pré-construídas
    log_info "Baixando imagens pré-construídas..."
    docker-compose -f docker-compose.simple.yml pull minio jupyter || log_warning "Algumas imagens podem não ter sido baixadas"
    
    # Iniciar serviços
    log_info "Iniciando serviços..."
    if docker-compose -f docker-compose.simple.yml up -d; then
        log_success "Serviços iniciados com sucesso!"
        
        echo ""
        echo "🎉 DataLab iniciado com sucesso!"
        echo "================================"
        echo "📊 MLflow: http://localhost:5000"
        echo "📓 Jupyter: http://localhost:8888 (token: datalab123)"
        echo "🗃️  MinIO: http://localhost:9001 (minioadmin/minioadmin)"
        echo "🌐 Streamlit: http://localhost:8501"
        echo ""
        echo "Para ver os logs: docker-compose -f docker-compose.simple.yml logs -f"
        echo "Para parar: docker-compose -f docker-compose.simple.yml down"
        
    else
        log_error "Falha ao iniciar os serviços"
        exit 1
    fi
}

# Função para mostrar ajuda
show_help() {
    echo "Uso: $0 [opção]"
    echo ""
    echo "Opções:"
    echo "  start     - Inicia os serviços (padrão)"
    echo "  stop      - Para os serviços"
    echo "  restart   - Reinicia os serviços"
    echo "  logs      - Mostra os logs"
    echo "  status    - Mostra o status dos serviços"
    echo "  clean     - Para e remove todos os containers e volumes"
    echo "  help      - Mostra esta ajuda"
}

# Processar argumentos
case "${1:-start}" in
    "start")
        main
        ;;
    "stop")
        log_info "Parando serviços..."
        docker-compose -f docker-compose.simple.yml down
        log_success "Serviços parados!"
        ;;
    "restart")
        log_info "Reiniciando serviços..."
        docker-compose -f docker-compose.simple.yml restart
        log_success "Serviços reiniciados!"
        ;;
    "logs")
        docker-compose -f docker-compose.simple.yml logs -f
        ;;
    "status")
        docker-compose -f docker-compose.simple.yml ps
        ;;
    "clean")
        log_warning "Parando e removendo todos os containers e volumes..."
        docker-compose -f docker-compose.simple.yml down -v --remove-orphans
        docker system prune -f
        log_success "Limpeza concluída!"
        ;;
    "help")
        show_help
        ;;
    *)
        log_error "Opção inválida: $1"
        show_help
        exit 1
        ;;
esac
