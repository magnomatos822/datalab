# Airbyte no DataFlow Lab

## Visão Geral

O [Airbyte](https://airbyte.com/) é uma plataforma de integração de dados de código aberto que permite sincronizar dados de diferentes fontes para destinos como data warehouses, lakes e bancos de dados. No contexto do DataFlow Lab, o Airbyte é utilizado para facilitar a ingestão de dados de várias fontes para a camada Bronze do nosso Data Lakehouse.

## Componentes Principais

- **Conectores de Origem**: Integração com mais de 200+ fontes de dados como bancos de dados, APIs, arquivos, etc.
- **Conectores de Destino**: Possibilidade de enviar dados para diversos destinos como MinIO, Data Lakes, etc.
- **UI Web**: Interface gráfica para configurar, monitorar e gerenciar conexões.
- **Scheduler**: Agendamento de sincronizações de dados em intervalos definidos.
- **API**: Permite automação e integração com outras ferramentas como o Prefect.

## Como Utilizar

### Acessando a Interface Web do Airbyte

1. Após iniciar o ambiente com `docker-compose up -d`, acesse:
   - URL: http://localhost:8000
   - Usuário padrão: `airbyte`
   - Senha padrão: `password`

### Configurando uma Nova Conexão

1. **Adicionar Fonte**:
   - Acesse "Sources" no menu lateral
   - Clique em "New Source"
   - Selecione o conector desejado (ex: MySQL, API, etc)
   - Configure as credenciais e parâmetros necessários

2. **Adicionar Destino**:
   - Acesse "Destinations" no menu lateral
   - Clique em "New Destination"
   - Para integração com o Data Lakehouse, configure:
     - Tipo: S3/MinIO
     - Endpoint: http://minio:9000
     - Bucket: `bronze`
     - Credenciais: Conforme definido no MinIO

3. **Criar Conexão**:
   - Acesse "Connections" no menu lateral
   - Clique em "New Connection"
   - Selecione a fonte e o destino criados anteriormente
   - Configure a frequência de sincronização
   - Selecione quais tabelas/dados sincronizar

### Integração com Prefect e Camada Bronze

O DataFlow Lab inclui integração automática entre o Airbyte e o Prefect para orquestrar fluxos de dados. Veja o exemplo abaixo de como criar um fluxo Prefect que executa sincronizações do Airbyte:

```python
from prefect import flow, task
import requests
import os
import json

@task
def trigger_airbyte_sync(connection_id):
    """Tarefa que dispara uma sincronização específica no Airbyte"""
    airbyte_api = "http://airbyte-server:8000/api/v1/connections/sync"
    headers = {"Content-Type": "application/json"}
    payload = {"connectionId": connection_id}
    
    response = requests.post(
        airbyte_api,
        headers=headers,
        data=json.dumps(payload)
    )
    
    if response.status_code == 200:
        job_id = response.json().get("job", {}).get("id")
        return job_id
    else:
        raise Exception(f"Erro ao acionar sincronização: {response.text}")

@flow(name="Airbyte to Bronze Flow")
def airbyte_to_bronze(connection_ids):
    """Fluxo que aciona múltiplas sincronizações no Airbyte"""
    job_ids = []
    for conn_id in connection_ids:
        job_id = trigger_airbyte_sync(conn_id)
        job_ids.append(job_id)
    
    return job_ids

# Exemplo de uso
if __name__ == "__main__":
    # IDs de conexão do Airbyte
    connection_ids = [
        "your-connection-id-1", 
        "your-connection-id-2"
    ]
    
    airbyte_to_bronze(connection_ids)
```

## Prática Recomendada: Configuração de Destino para Bronze Layer

Para manter a arquitetura Medallion consistente, configure seus destinos Airbyte para escrever no bucket `bronze` no MinIO com a seguinte estrutura de diretórios:

```
s3://bronze/airbyte/<source_name>/<table_name>/
```

## Solução de Problemas

- **Erro de Conexão**: Verifique se os serviços estão em execução corretamente com `docker-compose ps`
- **Falha na Sincronização**: Verifique os logs específicos da conexão na interface do Airbyte
- **Problema de Credenciais**: Verifique as permissões no MinIO e se as credenciais estão corretas

## Recursos Adicionais

- [Documentação Oficial do Airbyte](https://docs.airbyte.com/)
- [Conectores Disponíveis](https://docs.airbyte.com/integrations/)
- [API Reference do Airbyte](https://docs.airbyte.com/api-documentation)
