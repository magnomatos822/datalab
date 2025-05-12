# MinIO na Arquitetura DataFlow Lab

## Visão Geral

O MinIO é um servidor de armazenamento de objetos de alta performance, compatível com a API do Amazon S3. No contexto do DataFlow Lab, o MinIO serve como a camada de armazenamento fundamental para a implementação da arquitetura Medallion (Bronze, Silver, Gold).

## Características Principais

- **Compatibilidade S3**: Fornece uma API compatível com Amazon S3
- **Alta Performance**: Otimizado para grandes volumes de dados
- **Escalabilidade**: Pode ser escalado horizontalmente para lidar com petabytes de dados
- **WORM (Write Once Read Many)**: Suporte para imutabilidade de dados
- **Criptografia**: Criptografia em repouso e em trânsito
- **Retenção de objetos**: Políticas de retenção para compliance

## Configuração no DataFlow Lab

O MinIO é configurado com três buckets principais, correspondentes às camadas da arquitetura Medallion:

1. **bronze**: Armazena dados brutos, sem transformação ou com mínima transformação
2. **silver**: Armazena dados limpos e transformados
3. **gold**: Armazena dados agregados e refinados para consumo

## Acessando o MinIO

- **Console Web**: [http://localhost:9001](http://localhost:9001)
- **Credenciais**: 
  - Usuário: `admin`
  - Senha: `admin123`

## Endpoints

- **API S3**: [http://localhost:9000](http://localhost:9000)
- **Console**: [http://localhost:9001](http://localhost:9001)

## Uso com Spark

O Apache Spark está configurado para acessar o MinIO usando a biblioteca Hadoop S3A. Exemplo de código:

```python
# Leitura de dados do bucket bronze usando Delta Lake
bronze_df = spark.read.format("delta").load("s3a://bronze/meu_dataset")

# Escrita de dados no bucket silver usando Delta Lake
silver_df.write.format("delta").mode("overwrite").save("s3a://silver/meu_dataset")
```

## Buckets e Organização

A estrutura de diretórios recomendada para cada bucket é:

### Bronze

```
bronze/
├── raw_data_source1/
│   ├── table1/
│   └── table2/
├── raw_data_source2/
│   ├── table1/
│   └── table2/
└── logs/
```

### Silver

```
silver/
├── clean_data_domain1/
│   ├── table1/
│   └── table2/
├── clean_data_domain2/
│   ├── table1/
│   └── table2/
└── metrics/
```

### Gold

```
gold/
├── analytics_domain1/
│   ├── dashboard1/
│   └── dashboard2/
├── analytics_domain2/
│   ├── view1/
│   └── view2/
└── ml_features/
```

## Políticas de Retenção

As políticas de retenção são configuradas para cada bucket:

- **bronze**: 90 dias
- **silver**: 180 dias
- **gold**: 365 dias

## Monitoramento

O MinIO expõe métricas via Prometheus que podem ser visualizadas no Grafana. Endpoints:

- **Métricas Prometheus**: http://localhost:9000/minio/v2/metrics/cluster

## Backup e Recuperação

Para configurar backup:

1. Use o comando `mc mirror` para fazer backup dos buckets
2. Configure um job Prefect para automatizar o backup
3. Armazene backups em um local seguro

## Resolução de Problemas

Problemas comuns e soluções:

1. **Erro de Conexão**: Verifique se o MinIO está em execução com `docker ps | grep minio`
2. **Erro de Permissão**: Verifique as credenciais e permissões dos buckets
3. **Desempenho Lento**: Verifique a configuração de recursos do container

## Referências

- [Documentação Oficial do MinIO](https://min.io/docs/minio/linux/index.html)
- [Integração MinIO com Spark](https://docs.min.io/docs/how-to-use-spark-with-minio.html)
