#!/bin/bash

# Script de inicialização dos fluxos Prefect para o DataLab

set -e

echo "🔄 Inicializando fluxos Prefect para DataLab..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se o Prefect está disponível
log "Verificando conectividade com Prefect..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s -f http://localhost:4200/api/health > /dev/null 2>&1; then
        success "Prefect server está disponível"
        break
    else
        warning "Tentativa $attempt/$max_attempts - Aguardando Prefect server..."
        sleep 10
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    error "Prefect server não está disponível após ${max_attempts} tentativas"
    exit 1
fi

# Configurar variáveis de ambiente
export PREFECT_API_URL="http://localhost:4200/api"

# Criar work pool se não existir
log "Configurando work pool..."
prefect work-pool create default-agent-pool --type process || {
    warning "Work pool já existe ou erro na criação"
}

# Registrar fluxos
log "Registrando fluxos Prefect..."

# Fluxo ETL Medallion
log "Registrando Medallion ETL Pipeline..."
cd /opt/spark-apps/flows
python -c "
import sys
sys.path.append('/opt/spark-apps')
from medallion_etl_flow import medallion_etl_pipeline
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule

deployment = Deployment.build_from_flow(
    flow=medallion_etl_pipeline,
    name='medallion-etl-daily',
    version='1.0.0',
    schedule=CronSchedule(cron='0 6 * * *', timezone='America/Sao_Paulo'),
    work_pool_name='default-agent-pool',
    tags=['etl', 'medallion', 'daily', 'datalab'],
    parameters={
        'source_path': '/opt/spark-apps/data/stocks.csv',
        'enable_quality_checks': True,
        'min_rows_threshold': 1000
    }
)
deployment.apply()
print('✅ Medallion ETL deployment criado')
" || error "Erro ao registrar Medallion ETL"

# Fluxo de Monitoramento
log "Registrando Real-time Monitoring Pipeline..."
python -c "
import sys
sys.path.append('/opt/spark-apps')
from monitoring_flow import realtime_monitoring_flow
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule
from datetime import timedelta

deployment = Deployment.build_from_flow(
    flow=realtime_monitoring_flow,
    name='datalab-monitoring-realtime',
    version='1.0.0',
    schedule=IntervalSchedule(interval=timedelta(minutes=5)),
    work_pool_name='default-agent-pool',
    tags=['monitoring', 'realtime', 'health-check', 'datalab']
)
deployment.apply()
print('✅ Monitoring deployment criado')
" || error "Erro ao registrar Monitoring"

# Fluxo MLOps
log "Registrando MLOps Pipeline..."
python -c "
import sys
sys.path.append('/opt/spark-apps')
from mlops_flow import mlops_pipeline
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule

deployment = Deployment.build_from_flow(
    flow=mlops_pipeline,
    name='mlops-weekly-retrain',
    version='1.0.0',
    schedule=CronSchedule(cron='0 2 * * 0', timezone='America/Sao_Paulo'),
    work_pool_name='default-agent-pool',
    tags=['mlops', 'training', 'weekly', 'stock-prediction'],
    parameters={
        'data_path': 's3://gold/stocks_analytics/latest',
        'model_type': 'random_forest',
        'experiment_name': 'datalab-stock-prediction'
    }
)
deployment.apply()
print('✅ MLOps deployment criado')
" || error "Erro ao registrar MLOps"

# Fluxo de Manutenção
log "Registrando Data Lake Maintenance Pipeline..."
python -c "
import sys
sys.path.append('/opt/spark-apps')
from maintenance_flow import data_lake_maintenance_flow
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule

deployment = Deployment.build_from_flow(
    flow=data_lake_maintenance_flow,
    name='datalake-maintenance-weekly',
    version='1.0.0',
    schedule=CronSchedule(cron='0 3 * * 6', timezone='America/Sao_Paulo'),
    work_pool_name='default-agent-pool',
    tags=['maintenance', 'cleanup', 'weekly', 'datalake'],
    parameters={
        'retention_days': 30
    }
)
deployment.apply()
print('✅ Maintenance deployment criado')
" || error "Erro ao registrar Maintenance"

# Listar deployments criados
log "Listando deployments criados..."
prefect deployment ls

# Iniciar worker em background (opcional)
if [ "${START_WORKER:-false}" = "true" ]; then
    log "Iniciando Prefect worker em background..."
    nohup prefect worker start --pool default-agent-pool --type process > /tmp/prefect-worker.log 2>&1 &
    WORKER_PID=$!
    echo $WORKER_PID > /tmp/prefect-worker.pid
    success "Worker iniciado com PID: $WORKER_PID"
fi

success "🎉 Inicialização dos fluxos Prefect concluída!"

# Mostrar resumo
echo ""
echo "📊 RESUMO DOS FLUXOS REGISTRADOS:"
echo "=================================="
echo "🔄 Medallion ETL Pipeline    - Diário às 06:00"
echo "🔍 Real-time Monitoring      - A cada 5 minutos"  
echo "🤖 MLOps Training Pipeline   - Semanal (Domingo 02:00)"
echo "🧹 Data Lake Maintenance     - Semanal (Sábado 03:00)"
echo ""
echo "🌐 Acesse o Prefect UI em: http://localhost:4200"
echo "📚 Logs disponíveis em: /tmp/prefect-worker.log"
echo ""

exit 0
