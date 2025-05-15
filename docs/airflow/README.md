# Apache Airflow no DataLab

O Apache Airflow é uma plataforma de orquestração de fluxos de trabalho que permite programar, agendar e monitorar pipelines complexos de processamento de dados.

## Configuração

O Airflow no DataLab está configurado com os seguintes componentes:

- **airflow-webserver**: Interface de usuário do Airflow (porta 8070)
- **airflow-scheduler**: Responsável por agendar e iniciar execuções de fluxos de trabalho
- **airflow-postgres**: Banco de dados PostgreSQL para metadados do Airflow

## Acesso

- **Interface Web**: http://localhost:8070
- **Usuário padrão**: admin
- **Senha padrão**: admin

## Estrutura de Diretórios

```
./data/airflow/
│
├── dags/           # DAGs (fluxos de trabalho) do Airflow
├── logs/           # Logs gerados pelo Airflow
├── plugins/        # Plugins personalizados
├── config/         # Arquivos de configuração adicionais
└── postgres/       # Banco de dados PostgreSQL
```

## Integração com Outros Serviços

O Airflow foi configurado para se integrar facilmente com outros componentes do DataLab:

- **Apache Spark**: Configurado para executar tarefas de processamento distribuído
- **MinIO (S3)**: Para armazenamento de dados nos diferentes estágios da arquitetura Medallion
- **PostgreSQL**: Como banco de dados de metadados

## DAGs de Exemplo

### Arquitetura Medallion

O DataLab inclui um DAG de exemplo que implementa a arquitetura Medallion, organizando os dados em três camadas:

1. **Bronze**: Dados brutos ingeridos de fontes externas
2. **Silver**: Dados limpos e transformados
3. **Gold**: Dados agregados e prontos para consumo por analistas ou modelos de ML

Para implementar seus próprios DAGs, siga estas práticas:

1. Crie um novo arquivo Python na pasta `./data/airflow/dags/`
2. Defina seu DAG e tarefas seguindo as melhores práticas do Airflow
3. O scheduler detectará automaticamente o novo DAG

## Conexões

Para configurar novas conexões (por exemplo, para bancos de dados externos):

1. Acesse a interface web do Airflow
2. Navegue até Admin > Connections
3. Adicione uma nova conexão com as credenciais necessárias

## Manutenção

Para verificar logs ou solucionar problemas:

```bash
# Verificar logs do webserver
docker logs airflow-webserver

# Verificar logs do scheduler
docker logs airflow-scheduler
```

Para redefinir o banco de dados (em caso de problemas):

```bash
docker-compose stop airflow-webserver airflow-scheduler
docker-compose rm -f airflow-postgres
docker-compose up -d airflow-postgres
# Espere o PostgreSQL inicializar
docker-compose up -d airflow-webserver airflow-scheduler
```