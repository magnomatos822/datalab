#!/bin/bash

# Script de inicialização para configurações básicas do Apache NiFi no DataLab
# Este script pode ser executado dentro do container NiFi após a inicialização

echo "Configurando o Apache NiFi para integração com o DataLab..."

# Definir variáveis
MINIO_ENDPOINT=${MINIO_ENDPOINT:-http://minio:9000}
AWS_ACCESS_KEY=${AWS_ACCESS_KEY_ID:-minioadmin}
AWS_SECRET_KEY=${AWS_SECRET_ACCESS_KEY:-minioadmin}
SPARK_MASTER=${SPARK_MASTER_URL:-spark://spark-master:7077}

# Verificar a conectividade com outros serviços
echo "Verificando conectividade com MinIO..."
curl -s $MINIO_ENDPOINT/minio/health/live > /dev/null
if [ $? -eq 0 ]; then
    echo "MinIO está acessível"
else
    echo "ATENÇÃO: Não foi possível conectar ao MinIO"
fi

echo "Verificando conectividade com Spark Master..."
curl -s $SPARK_MASTER > /dev/null
if [ $? -eq 0 ]; then
    echo "Spark Master está acessível"
else
    echo "ATENÇÃO: Não foi possível conectar ao Spark Master"
fi

# Configurar diretórios de trabalho
mkdir -p /tmp/nifi/work
chmod -R 755 /tmp/nifi

echo "Apache NiFi configurado com sucesso para o ambiente DataLab!"
echo "Use a interface web para criar seus fluxos de dados e integrações."