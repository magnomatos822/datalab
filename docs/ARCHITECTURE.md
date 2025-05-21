# Arquitetura Desacoplada do DataLab

## Visão Geral

A arquitetura do DataLab foi redesenhada para proporcionar maior desacoplamento e escalabilidade. 
Agora, os serviços estão organizados em arquivos Docker Compose separados por funcionalidade, 
permitindo iniciar apenas os serviços necessários para cada caso de uso.

## Estrutura de Arquivos

- `docker-compose.core.yml`: Serviços de infraestrutura básica
  - MinIO (armazenamento de objetos)
  - Kafka (mensageria)
  - Consul (service discovery)

- `docker-compose.processing.yml`: Serviços de processamento de dados
  - Apache Spark (processamento distribuído)
  - Apache NiFi (automação de fluxo de dados)

- `docker-compose.ml.yml`: Serviços de machine learning
  - MLflow (gestão do ciclo de vida de ML)
  - Prefect (orquestração de workflows)
  - Airflow (orquestração de workflows)

- `docker-compose.visualization.yml`: Serviços de visualização de dados
  - JupyterHub (notebooks interativos)
  - Streamlit (aplicações de dados)

- `docker-compose.monitoring.yml`: Serviços de monitoramento
  - Prometheus (métricas)
  - Grafana (dashboards)

## Melhorias Implementadas

### 1. Balanceamento de Carga

O serviço Spark Worker foi configurado com:
- 3 réplicas para balanceamento de carga
- Limites de recursos definidos (CPU e memória)
- Reservas de recursos para garantir disponibilidade

### 2. Service Discovery com Consul

Todos os serviços foram configurados para:
- Registrar-se automaticamente no Consul
- Permitir descoberta dinâmica de serviços
- Usar a variável de ambiente `SERVICE_DISCOVERY_CONSUL=consul:8500`

### 3. Separação de Ambientes

Os ambientes agora podem ser iniciados separadamente através do script `scripts/manage_environments.sh`.

Exemplos de uso:
```bash
./scripts/manage_environments.sh start core       # Inicia apenas os serviços core
./scripts/manage_environments.sh start core ml    # Inicia os serviços core e ml
./scripts/manage_environments.sh start all        # Inicia todos os serviços
./scripts/manage_environments.sh stop ml          # Para os serviços ml
./scripts/manage_environments.sh status           # Mostra o status dos contêineres
```

## Rede

Todos os serviços compartilham a rede `dataflow-network` para permitir a comunicação entre contêineres 
em diferentes arquivos Docker Compose.

## Próximos Passos

1. Configurar logs centralizados para todos os serviços
2. Implementar autoscaling baseado em métricas
3. Configurar backups automatizados para os volumes persistentes
4. Implementar mais dashboards no Grafana para monitoramento avançado
