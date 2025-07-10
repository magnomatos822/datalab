#!/bin/bash

# Script de Inicialização Completa da Plataforma DataLab
# Executa todos os serviços e testa a integração

echo "🚀 Iniciando Plataforma DataLab Unificada..."

# Verificar dependências
echo "📋 Verificando dependências..."
python3 --version || { echo "❌ Python3 não encontrado"; exit 1; }
docker --version || { echo "❌ Docker não encontrado"; exit 1; }
docker-compose --version || { echo "❌ Docker Compose não encontrado"; exit 1; }

# Criar diretórios necessários
echo "📁 Criando estrutura de diretórios..."
mkdir -p logs
mkdir -p data/{bronze,silver,gold,raw}
mkdir -p models
mkdir -p notebooks/outputs

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

# Configurar variáveis de ambiente
echo "⚙️ Configurando ambiente..."
export PYTHONPATH="$PWD:$PWD/app:$PWD/core:$PWD/flows:$PYTHONPATH"

# Inicializar serviços Docker
echo "🐳 Iniciando serviços Docker..."
docker-compose -f docker-compose.yml up -d --remove-orphans

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Testar conectividade dos serviços
echo "🔍 Testando conectividade dos serviços..."

# MinIO
echo "  📦 Testando MinIO..."
curl -s http://localhost:9001 > /dev/null && echo "    ✅ MinIO disponível" || echo "    ❌ MinIO indisponível"

# Spark UI
echo "  ⚡ Testando Spark..."
curl -s http://localhost:4040 > /dev/null && echo "    ✅ Spark disponível" || echo "    ❌ Spark indisponível"

# Kafka
echo "  📡 Testando Kafka..."
docker-compose exec -T kafka kafka-topics.sh --bootstrap-server localhost:9092 --list > /dev/null 2>&1 && echo "    ✅ Kafka disponível" || echo "    ❌ Kafka indisponível"

# MLflow
echo "  🤖 Testando MLflow..."
curl -s http://localhost:5000 > /dev/null && echo "    ✅ MLflow disponível" || echo "    ❌ MLflow indisponível"

# JupyterHub
echo "  📓 Testando JupyterHub..."
curl -s http://localhost:8000 > /dev/null && echo "    ✅ JupyterHub disponível" || echo "    ❌ JupyterHub indisponível"

# Prefect
echo "  🌊 Testando Prefect..."
curl -s http://localhost:4200 > /dev/null && echo "    ✅ Prefect disponível" || echo "    ❌ Prefect indisponível"

# Inicializar Prefect flows
echo "🌊 Inicializando Prefect flows..."
if [ -f "flows/init_prefect_flows.sh" ]; then
    chmod +x flows/init_prefect_flows.sh
    ./flows/init_prefect_flows.sh
else
    echo "  ⚠️ Script de inicialização do Prefect não encontrado"
fi

# Configurar e testar plataforma unificada
echo "🌟 Testando plataforma unificada..."
python3 test_platform.py

# Iniciar Streamlit em segundo plano
echo "📊 Iniciando dashboard Streamlit..."
nohup streamlit run app/app.py --server.port 8501 --server.address 0.0.0.0 > logs/streamlit.log 2>&1 &
echo $! > logs/streamlit.pid

# Aguardar Streamlit inicializar
sleep 10

# Testar Streamlit
curl -s http://localhost:8501 > /dev/null && echo "    ✅ Streamlit disponível" || echo "    ❌ Streamlit indisponível"

echo ""
echo "🎉 Inicialização da Plataforma DataLab Concluída!"
echo ""
echo "📊 Acesse os serviços:"
echo "  • Dashboard Streamlit: http://localhost:8501"
echo "  • MinIO Console: http://localhost:9001 (admin/password123)"
echo "  • MLflow UI: http://localhost:5000"
echo "  • JupyterHub: http://localhost:8000 (admin/admin)"
echo "  • Prefect UI: http://localhost:4200"
echo "  • Spark UI: http://localhost:4040"
echo ""
echo "🛠️ Comandos úteis:"
echo "  • python datalab_cli.py --help                 # CLI da plataforma"
echo "  • python datalab_manager.py                    # Gerenciador principal"
echo "  • python test_platform.py                      # Testes da plataforma"
echo "  • docker-compose logs -f [service]             # Logs de serviços"
echo "  • python flows/medallion_etl_flow.py           # Executar ETL"
echo ""
echo "🔧 Para parar todos os serviços:"
echo "  • ./shutdown_platform.sh"
echo ""
