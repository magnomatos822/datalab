#!/bin/bash
# DataLab Platform Setup Script
# Script automatizado para configuração completa da plataforma

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "Este script não deve ser executado como root"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log_info "Verificando requisitos do sistema..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "Sistema Linux detectado"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_success "Sistema macOS detectado"
    else
        log_error "Sistema operacional não suportado: $OSTYPE"
        exit 1
    fi
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
            log_success "Python $PYTHON_VERSION encontrado"
        else
            log_error "Python 3.8+ é necessário (encontrado: $PYTHON_VERSION)"
            exit 1
        fi
    else
        log_error "Python3 não encontrado"
        exit 1
    fi
    
    # Check Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        log_success "Docker $DOCKER_VERSION encontrado"
    else
        log_error "Docker não encontrado"
        log_info "Por favor, instale o Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        log_success "Docker Compose $COMPOSE_VERSION encontrado"
    else
        log_error "Docker Compose não encontrado"
        log_info "Por favor, instale o Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check available disk space (minimum 10GB)
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    AVAILABLE_GB=$((AVAILABLE_SPACE / 1024 / 1024))
    
    if [ $AVAILABLE_GB -lt 10 ]; then
        log_warning "Espaço em disco baixo: ${AVAILABLE_GB}GB disponível (recomendado: 10GB+)"
    else
        log_success "Espaço em disco suficiente: ${AVAILABLE_GB}GB disponível"
    fi
    
    # Check available memory (minimum 4GB)
    if command -v free &> /dev/null; then
        AVAILABLE_MEM=$(free -m | awk 'NR==2{print $2}')
        AVAILABLE_MEM_GB=$((AVAILABLE_MEM / 1024))
        
        if [ $AVAILABLE_MEM_GB -lt 4 ]; then
            log_warning "Memória RAM baixa: ${AVAILABLE_MEM_GB}GB disponível (recomendado: 4GB+)"
        else
            log_success "Memória RAM suficiente: ${AVAILABLE_MEM_GB}GB disponível"
        fi
    fi
}

# Setup Python environment
setup_python_env() {
    log_info "Configurando ambiente Python..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Criando ambiente virtual Python..."
        python3 -m venv venv
        log_success "Ambiente virtual criado"
    else
        log_info "Ambiente virtual já existe"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    log_info "Atualizando pip..."
    pip install --upgrade pip
    
    # Install requirements
    log_info "Instalando dependências Python..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        log_success "Dependências Python instaladas"
    else
        log_error "Arquivo requirements.txt não encontrado"
        exit 1
    fi
}

# Setup configuration files
setup_configuration() {
    log_info "Configurando arquivos de configuração..."
    
    # Create config directories
    mkdir -p config/env
    mkdir -p logs
    mkdir -p data/{bronze,silver,gold}
    mkdir -p notebooks/shared
    mkdir -p models/{staging,production}
    mkdir -p scripts/automation
    mkdir -p backups
    
    # Generate environment configuration
    cat > config/env/development.yaml << EOF
# DataLab Development Environment Configuration
platform:
  debug: true
  log_level: DEBUG
  enable_profiling: true

services:
  prefect:
    workers: 1
    log_level: DEBUG
  
  spark:
    executor_memory: "1g"
    driver_memory: "512m"
    executor_cores: 1
  
  minio:
    console_enabled: true
  
  mlflow:
    tracking_enabled: true
    model_registry_enabled: true

monitoring:
  health_check_interval: 30
  metrics_enabled: true
  alerts_enabled: false

security:
  authentication: false
  authorization: false
  encryption: false
EOF
    
    # Generate production configuration
    cat > config/env/production.yaml << EOF
# DataLab Production Environment Configuration
platform:
  debug: false
  log_level: INFO
  enable_profiling: false

services:
  prefect:
    workers: 4
    log_level: INFO
  
  spark:
    executor_memory: "4g"
    driver_memory: "2g"
    executor_cores: 2
  
  minio:
    console_enabled: false
  
  mlflow:
    tracking_enabled: true
    model_registry_enabled: true

monitoring:
  health_check_interval: 60
  metrics_enabled: true
  alerts_enabled: true

security:
  authentication: true
  authorization: true
  encryption: true
EOF
    
    log_success "Arquivos de configuração criados"
}

# Setup Docker environment
setup_docker() {
    log_info "Configurando ambiente Docker..."
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon não está rodando"
        log_info "Por favor, inicie o Docker e tente novamente"
        exit 1
    fi
    
    # Create Docker network if it doesn't exist
    if ! docker network ls | grep -q "datalab-network"; then
        log_info "Criando rede Docker datalab-network..."
        docker network create datalab-network
        log_success "Rede Docker criada"
    else
        log_info "Rede Docker já existe"
    fi
    
    # Pull base images
    log_info "Baixando imagens Docker base..."
    docker pull python:3.11-slim
    docker pull bitnami/spark:3.5
    docker pull minio/minio:latest
    docker pull prefecthq/prefect:2.14.11-python3.11
    docker pull jupyterhub/jupyterhub:latest
    
    log_success "Imagens Docker baixadas"
}

# Initialize platform
initialize_platform() {
    log_info "Inicializando plataforma DataLab..."
    
    # Make scripts executable
    chmod +x datalab_manager.py
    chmod +x datalab_cli.py
    
    # Run platform initialization
    python3 datalab_manager.py status
    
    log_success "Plataforma DataLab inicializada"
}

# Create desktop shortcuts (Linux only)
create_shortcuts() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "Criando atalhos no desktop..."
        
        DESKTOP_DIR="$HOME/Desktop"
        if [ -d "$DESKTOP_DIR" ]; then
            cat > "$DESKTOP_DIR/DataLab Platform.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=DataLab Platform
Comment=Launch DataLab Data Platform
Exec=$(pwd)/datalab_manager.py start
Icon=applications-science
Terminal=true
Categories=Development;Science;
EOF
            chmod +x "$DESKTOP_DIR/DataLab Platform.desktop"
            log_success "Atalho criado no desktop"
        fi
    fi
}

# Display final instructions
show_final_instructions() {
    log_success "🎉 Setup da DataLab Platform concluído!"
    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    log_info "📋 Próximos passos:"
    echo
    echo "1. 🚀 Para iniciar a plataforma:"
    echo "   ${GREEN}./datalab_manager.py start${NC}"
    echo
    echo "2. 🔧 Para usar a CLI de gestão:"
    echo "   ${GREEN}./datalab_cli.py --help${NC}"
    echo
    echo "3. 📊 Para verificar status:"
    echo "   ${GREEN}./datalab_manager.py status${NC}"
    echo
    echo "4. 🌐 Interfaces web disponíveis após iniciar:"
    echo "   • Dashboard Streamlit:  ${BLUE}http://localhost:8501${NC}"
    echo "   • Prefect UI:          ${BLUE}http://localhost:4200${NC}"
    echo "   • JupyterHub:          ${BLUE}http://localhost:8000${NC}"
    echo "   • MinIO Console:       ${BLUE}http://localhost:9001${NC}"
    echo "   • MLflow UI:           ${BLUE}http://localhost:5000${NC}"
    echo "   • Spark UI:            ${BLUE}http://localhost:8080${NC}"
    echo
    echo "5. 📚 Documentação:"
    echo "   • README.md"
    echo "   • docs/README.md"
    echo "   • PREFECT_INTEGRATION_SUMMARY.md"
    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    log_success "✨ DataLab Platform está pronta para uso!"
}

# Main execution
main() {
    echo "🚀 DataLab Platform Setup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Check if not running as root
    check_root
    
    # Check system requirements
    check_requirements
    
    # Setup Python environment
    setup_python_env
    
    # Setup configuration
    setup_configuration
    
    # Setup Docker
    setup_docker
    
    # Initialize platform
    initialize_platform
    
    # Create shortcuts
    create_shortcuts
    
    # Show final instructions
    show_final_instructions
}

# Parse command line arguments
SKIP_DOCKER=false
DEVELOPMENT_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --dev)
            DEVELOPMENT_MODE=true
            shift
            ;;
        --help|-h)
            echo "DataLab Platform Setup Script"
            echo
            echo "Usage: $0 [options]"
            echo
            echo "Options:"
            echo "  --skip-docker    Skip Docker setup and image pulling"
            echo "  --dev           Setup for development mode"
            echo "  --help, -h      Show this help message"
            echo
            exit 0
            ;;
        *)
            log_error "Opção desconhecida: $1"
            exit 1
            ;;
    esac
done

# Set environment based on mode
if [ "$DEVELOPMENT_MODE" = true ]; then
    export DATALAB_ENV=development
    log_info "Modo de desenvolvimento ativado"
else
    export DATALAB_ENV=production
fi

# Skip Docker setup if requested
if [ "$SKIP_DOCKER" = true ]; then
    log_warning "Pulando configuração do Docker"
    setup_docker() {
        log_info "Configuração do Docker pulada"
    }
fi

# Run main function
main

echo
log_success "🎯 Setup concluído com sucesso!"
exit 0
