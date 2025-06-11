#!/bin/bash

# Script de inicialização do JupyterHub
# Cria usuários do sistema para autenticação PAM

echo "🚀 Iniciando configuração do JupyterHub..."

# Criar usuários do sistema se não existirem
echo "👤 Criando usuários do sistema..."

# Criar usuário magnomatos822
if ! id "magnomatos822" &>/dev/null; then
    useradd -m -s /bin/bash magnomatos822
    echo "magnomatos822:datalab" | chpasswd
    echo "✅ Usuário magnomatos822 criado com senha: datalab"
else
    echo "👤 Usuário magnomatos822 já existe"
    echo "magnomatos822:datalab" | chpasswd
    echo "🔐 Senha do usuário magnomatos822 atualizada para: datalab"
fi

# Criar usuário admin
if ! id "admin" &>/dev/null; then
    useradd -m -s /bin/bash admin
    echo "admin:datalab" | chpasswd
    echo "✅ Usuário admin criado com senha: datalab"
else
    echo "👤 Usuário admin já existe"
    echo "admin:datalab" | chpasswd
    echo "🔐 Senha do usuário admin atualizada para: datalab"
fi

# Garantir que os diretórios home existem e têm permissões corretas
mkdir -p /home/magnomatos822
mkdir -p /home/admin
mkdir -p /home/jovyan/work

chown magnomatos822:magnomatos822 /home/magnomatos822
chown admin:admin /home/admin
chmod 755 /home/magnomatos822 /home/admin

echo "📁 Diretórios home configurados"

# Instalar dependências necessárias
echo "📦 Instalando dependências..."
apt-get update -qq
apt-get install -y --no-install-recommends curl docker.io

# Instalar pacotes Python necessários
pip install notebook jupyterlab jupyterhub-idle-culler
pip install jupyterhub oauthenticator dockerspawner

echo "🎯 Configuração concluída! Iniciando JupyterHub..."

# Iniciar JupyterHub
exec jupyterhub -f /srv/jupyterhub/jupyterhub_config.py
