#!/bin/bash

# Script para inicializar buckets do MinIO para a arquitetura Medallion
#
# Este script cria os três buckets da arquitetura Medallion:
# - bronze: Dados brutos, sem transformações significativas
# - silver: Dados limpos e transformados
# - gold: Dados agregados e refinados para consumo
#
# E também o bucket para o MLflow:
# - mlflow: Artefatos de experimentos do MLflow

# Configurações
MINIO_HOST="localhost:9000"
ACCESS_KEY="admin"
SECRET_KEY="admin123"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Iniciando configuração dos buckets do MinIO...${NC}"

# Verificar se mc (cliente MinIO) está instalado
if ! command -v mc &> /dev/null
then
    echo -e "${RED}mc (cliente MinIO) não encontrado. Instalando...${NC}"
    wget https://dl.min.io/client/mc/release/linux-amd64/mc
    chmod +x mc
    sudo mv mc /usr/local/bin/
fi

# Configurar cliente MinIO
echo -e "${YELLOW}Configurando cliente MinIO...${NC}"
mc config host add minio-local http://${MINIO_HOST} ${ACCESS_KEY} ${SECRET_KEY}

# Verificar se a configuração foi bem-sucedida
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao configurar cliente MinIO. Verifique se o servidor MinIO está em execução.${NC}"
    exit 1
fi

# Criar buckets se não existirem
echo -e "${YELLOW}Criando bucket bronze...${NC}"
mc mb minio-local/bronze --ignore-existing

echo -e "${YELLOW}Criando bucket silver...${NC}"
mc mb minio-local/silver --ignore-existing

echo -e "${YELLOW}Criando bucket gold...${NC}"
mc mb minio-local/gold --ignore-existing

echo -e "${YELLOW}Criando bucket mlflow...${NC}"
mc mb minio-local/mlflow --ignore-existing

# Verificar se os buckets foram criados corretamente
echo -e "${YELLOW}Verificando buckets criados:${NC}"
mc ls minio-local

# Configurar políticas de acesso
echo -e "${YELLOW}Configurando políticas de acesso...${NC}"

# Política para leitura pública do bucket gold (para dashboards)
cat > /tmp/gold-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": ["*"]
      },
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::gold/*"]
    }
  ]
}
EOF

# Aplicar política
mc policy set-json /tmp/gold-policy.json minio-local/gold

echo -e "${GREEN}Buckets da arquitetura Medallion criados e configurados com sucesso!${NC}"
echo -e "${GREEN}Estrutura Medallion pronta para uso.${NC}"

# Criar estrutura de diretórios de exemplo
echo -e "${YELLOW}Criando estrutura de diretórios de exemplo...${NC}"

# Exemplo de estrutura para bronze
mc mkdir -p minio-local/bronze/raw_data_source1/table1
mc mkdir -p minio-local/bronze/raw_data_source2/table1
mc mkdir -p minio-local/bronze/logs

# Exemplo de estrutura para silver
mc mkdir -p minio-local/silver/clean_data_domain1/table1
mc mkdir -p minio-local/silver/clean_data_domain2/table1
mc mkdir -p minio-local/silver/metrics

# Exemplo de estrutura para gold
mc mkdir -p minio-local/gold/analytics_domain1/dashboard1
mc mkdir -p minio-local/gold/analytics_domain2/view1
mc mkdir -p minio-local/gold/ml_features

# Estrutura para MLflow
mc mkdir -p minio-local/mlflow/artifacts
mc mkdir -p minio-local/mlflow/models

echo -e "${GREEN}Estrutura de diretórios de exemplo criada com sucesso!${NC}"
echo -e "${YELLOW}Acesse a interface web do MinIO em: http://localhost:9001${NC}"
echo -e "${YELLOW}Usuário: ${ACCESS_KEY}, Senha: ${SECRET_KEY}${NC}"
