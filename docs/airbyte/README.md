# Airbyte no DataLab

O Airbyte é uma plataforma de integração de dados de código aberto que permite conectar fontes de dados a destinos de forma rápida e confiável.

## Funcionalidades

- Sincronização de dados entre diferentes fontes e destinos
- Interface visual para configuração de conexões 
- Mais de 300 conectores pré-construídos
- Transformações de dados via SQL ou dbt
- Orquestração de fluxos de dados
- Monitoramento de jobs de sincronização

## Como acessar

O Airbyte está disponível na URL:
```
http://localhost:8000
```

## Credenciais padrão

Ao iniciar o Airbyte pela primeira vez, você precisará criar suas credenciais de acesso.

## Integrações com o DataLab

O Airbyte está integrado com outros componentes do DataLab:

- **Minio (S3)**: Pode ser usado como destino para dados sincronizados
- **Postgres**: Pode ser usado como fonte ou destino para dados sincronizados
- **Spark**: Pode processar dados exportados pelo Airbyte
- **Airflow**: Pode orquestrar sincronizações do Airbyte

## Casos de uso comuns

1. **Ingestão de dados para a camada Bronze**:
   - Configure fontes de dados no Airbyte (APIs, bancos de dados, etc.)
   - Configure o MinIO como destino usando o conector S3
   - Direcione para buckets na camada bronze do data lake

2. **ETL para bancos de dados**:
   - Sincronize dados de diferentes fontes
   - Use transformações SQL para normalizar os dados
   - Armazene os resultados no Postgres ou outro banco de dados

3. **Conexão com plataformas SaaS**:
   - Sincronize dados de plataformas como Salesforce, Google Analytics, etc.
   - Combine-os com outras fontes de dados no data lake

## Configuração de uma nova conexão

1. Acesse a interface web do Airbyte em http://localhost:8000
2. Navegue até "Sources" e clique em "New source"
3. Selecione o conector desejado e configure os parâmetros necessários
4. Navegue até "Destinations" e clique em "New destination"
5. Selecione o conector desejado e configure os parâmetros
6. Crie uma nova conexão entre a fonte e o destino
7. Configure a frequência de sincronização e outras opções

## Dicas para uso no DataLab

- Para conectar ao MinIO como destino S3, use o endpoint `http://minio:9000`
- Para conectar ao Postgres como destino, use o host `postgres-airflow` e porta `5432`
- Os dados ingeridos via Airbyte podem ser processados posteriormente com Spark ou transformados com dbt

## Recursos úteis

- [Documentação oficial do Airbyte](https://docs.airbyte.com/)
- [Conectores disponíveis](https://docs.airbyte.com/integrations/)
- [Tutorial de orquestração com Airflow](https://airbyte.com/tutorials/airflow-airbyte)