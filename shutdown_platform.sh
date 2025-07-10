#!/bin/bash

# Script para parar todos os serviços da plataforma DataLab

echo "🛑 Parando Plataforma DataLab..."

# Parar Streamlit
echo "📊 Parando Streamlit..."
if [ -f "logs/streamlit.pid" ]; then
    kill $(cat logs/streamlit.pid) 2>/dev/null
    rm logs/streamlit.pid
    echo "  ✅ Streamlit parado"
else
    echo "  ⚠️ PID do Streamlit não encontrado"
fi

# Parar serviços Docker
echo "🐳 Parando serviços Docker..."
docker-compose -f docker-compose.yml down

# Limpeza opcional
read -p "🗑️ Remover volumes Docker? (dados serão perdidos) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ Removendo volumes..."
    docker-compose -f docker-compose.yml down -v
    echo "  ✅ Volumes removidos"
fi

# Limpeza de processos Python relacionados
echo "🧹 Limpando processos Python..."
pkill -f "streamlit run" 2>/dev/null
pkill -f "prefect" 2>/dev/null

echo ""
echo "✅ Plataforma DataLab parada com sucesso!"
echo ""
echo "💡 Para reiniciar:"
echo "  ./start_platform.sh"
echo ""
