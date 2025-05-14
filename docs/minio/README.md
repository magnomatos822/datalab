# MinIO - Armazenamento de Objetos Compatível com S3

<div align="center">
  <img src="https://img.shields.io/badge/MinIO-C72E49?style=for-the-badge&logo=minio&logoColor=white" alt="MinIO">
</div>

> Versão: RELEASE.2025-04-22T22-12-26Z

## O que é MinIO?

MinIO é um servidor de armazenamento de objetos de alto desempenho, compatível com a API Amazon S3. É projetado para ambientes de nuvem privada, oferecendo escalabilidade horizontal, resiliência e performance para cargas de trabalho de dados de qualquer tamanho.

No DataFlow Lab, o MinIO serve como a espinha dorsal de armazenamento do Data Lakehouse, fornecendo o armazenamento persistente para as camadas Bronze, Silver e Gold da arquitetura Medallion.

## Características Principais

- **Compatibilidade com S3**: API totalmente compatível com AWS S3
- **Alta Performance**: Otimizado para cargas de trabalho analíticas
- **Escalabilidade**: Suporta bilhões de objetos
- **Segurança**: Criptografia em repouso e em trânsito
- **Consistência**: Consistência forte de leitura após escrita
- **Multitenancy**: Gerenciamento por buckets e usuários

## Como Acessar

O MinIO está disponível em:

- **API S3**: [http://localhost:9000](http://localhost:9000)
- **Console Web**: [http://localhost:9001](http://localhost:9001)
- **Credenciais Padrão**:
  - Username: admin
  - Password: admin123

## Estrutura do Data Lake

No DataFlow Lab, o MinIO é organizado seguindo a arquitetura Medallion com as seguintes camadas:

```
MinIO
├── bronze/                # Dados brutos ingeridos
│   ├── logs/              # Logs de sistemas e aplicações
│   ├── raw_data_source1/  # Fonte de dados brutos 1
│   │   └── table1/        # Tabela/coleção específica
│   └── raw_data_source2/  # Fonte de dados brutos 2
│       └── table1/        # Tabela/coleção específica
│
├── silver/                # Dados limpos e processados
│   ├── clean_data_domain1/  # Domínio 1 de dados limpos
│   │   └── table1/        # Tabela/coleção específica
│   ├── clean_data_domain2/  # Domínio 2 de dados limpos
│   │   └── table1/        # Tabela/coleção específica
│   └── metrics/           # Métricas calculadas
│
├── gold/                  # Dados agregados e para consumo
│   ├── analytics_domain1/ # Domínio analítico 1
│   │   └── dashboard1/    # Dados para dashboard específico
│   ├── analytics_domain2/ # Domínio analítico 2
│   │   └── view1/         # Visualização específica
│   └── ml_features/       # Features para ML
│
└── mlflow/                # Armazenamento para MLflow
    ├── artifacts/         # Artefatos de experimentos
    └── models/            # Modelos treinados
```

## Uso do MinIO no DataFlow Lab

### Acesso Programático com Python

```python
import boto3
from botocore.client import Config

# Conectar ao MinIO
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='admin',
    aws_secret_access_key='admin123',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

# Listar buckets
response = s3_client.list_buckets()
for bucket in response['Buckets']:
    print(f"Bucket: {bucket['Name']}")

# Upload de arquivo
s3_client.upload_file(
    'data/sample.csv', 
    'bronze', 
    'raw_data_source1/table1/sample.csv'
)

# Download de arquivo
s3_client.download_file(
    'silver', 
    'clean_data_domain1/table1/processed.csv',
    'data/processed.csv'
)

# Listar objetos em um bucket/prefixo
response = s3_client.list_objects_v2(
    Bucket='bronze',
    Prefix='raw_data_source1/table1/'
)

for obj in response.get('Contents', []):
    print(f"Object: {obj['Key']}, Size: {obj['Size']} bytes")
```

### Acesso via PySpark

```python
from pyspark.sql import SparkSession

# Configurar SparkSession com acesso ao MinIO
spark = SparkSession.builder \
    .appName("MinIO-Data-Access") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "admin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Ler dados diretamente do MinIO
df = spark.read.csv("s3a://bronze/raw_data_source1/table1/sample.csv", header=True)

# Processar dados
df_processed = df.filter(df.value > 0).withColumn("processed_date", current_date())

# Escrever resultados de volta para o MinIO (formato Delta)
df_processed.write \
    .format("delta") \
    .mode("overwrite") \
    .save("s3a://silver/clean_data_domain1/table1")
```

### Acesso via Prefect

```python
from prefect import task, flow
import boto3
from botocore.client import Config

@task
def list_files_in_minio(bucket, prefix):
    s3_client = boto3.client(
        's3',
        endpoint_url='http://minio:9000',
        aws_access_key_id='admin',
        aws_secret_access_key='admin123',
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )
    
    response = s3_client.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix
    )
    
    files = [obj['Key'] for obj in response.get('Contents', [])]
    return files

@task
def process_file(bucket, file_key, output_bucket, output_prefix):
    # Lógica de processamento
    # ...
    return f"{output_bucket}/{output_prefix}/{file_key.split('/')[-1]}"

@flow
def process_minio_files():
    # Listar arquivos na camada Bronze
    files = list_files_in_minio(
        bucket="bronze", 
        prefix="raw_data_source1/table1/"
    )
    
    # Processar cada arquivo
    results = []
    for file_key in files:
        result = process_file(
            bucket="bronze",
            file_key=file_key,
            output_bucket="silver",
            output_prefix="clean_data_domain1/table1"
        )
        results.append(result)
        
    return results
```

## Administração do MinIO

### Buckets e Políticas

Para criar buckets e configurar políticas via console MinIO:

1. Acesse o console MinIO [http://localhost:9001](http://localhost:9001)
2. Faça login com as credenciais (admin/admin123)
3. Navegue até "Buckets" no menu lateral
4. Clique em "Create Bucket+"
5. Para configurar políticas, clique no bucket → Manage → Access Policy

### Versionamento e Retenção

O MinIO suporta versionamento de objetos, recurso crucial para implementações Data Lakehouse:

```python
# Habilitar versionamento em um bucket
s3_client.put_bucket_versioning(
    Bucket='bronze',
    VersioningConfiguration={'Status': 'Enabled'}
)

# Recuperar versão específica de um objeto
s3_client.get_object(
    Bucket='bronze',
    Key='raw_data_source1/table1/data.csv',
    VersionId='specific-version-id'
)
```

### Monitoramento

Estatísticas de uso e monitoramento:

1. No console MinIO: Metrics → Dashboard
2. API para métricas: http://localhost:9000/minio/v2/metrics/cluster

## Integração com Arquitetura Medallion

A arquitetura Medallion no DataFlow Lab utiliza o MinIO como base de armazenamento:

1. **Ingestão na camada Bronze**:
   ```python
   # Via Apache NiFi ou Python
   # Dados armazenados como arquivos brutos
   s3_client.upload_file('source.csv', 'bronze', 'raw_data_source1/table1/source.csv')
   ```

2. **Processamento para camada Silver**:
   ```python
   # Via Spark
   bronze_df = spark.read.format("delta").load("s3a://bronze/raw_data_source1/table1")
   silver_df = bronze_df.dropna().withColumn("processed_ts", current_timestamp())
   silver_df.write.format("delta").save("s3a://silver/clean_data_domain1/table1")
   ```

3. **Agregações para camada Gold**:
   ```python
   # Via Spark
   silver_df = spark.read.format("delta").load("s3a://silver/clean_data_domain1/table1")
   gold_df = silver_df.groupBy("category").agg(sum("amount").alias("total_amount"))
   gold_df.write.format("delta").save("s3a://gold/analytics_domain1/category_totals")
   ```

## Sincronização de Dados

Para sincronizar dados do sistema de arquivos local para o MinIO:

```bash
# Usando a ferramenta mc (MinIO Client)
mc config host add datalab http://localhost:9000 admin admin123
mc mirror --watch local-folder/ datalab/bronze/raw_data_source1/
```

Via Python com observação contínua:

```python
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, s3_client, bucket, prefix):
        self.s3_client = s3_client
        self.bucket = bucket
        self.prefix = prefix

    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        file_name = os.path.basename(file_path)
        s3_key = f"{self.prefix}/{file_name}"
        
        print(f"Uploading {file_path} to s3://{self.bucket}/{s3_key}")
        self.s3_client.upload_file(file_path, self.bucket, s3_key)

# Configurar cliente S3
s3_client = boto3.client('s3', 
                        endpoint_url='http://localhost:9000',
                        aws_access_key_id='admin',
                        aws_secret_access_key='admin123',
                        config=Config(signature_version='s3v4'))

# Configurar observador
event_handler = NewFileHandler(s3_client, "bronze", "raw_data_source1/table1")
observer = Observer()
observer.schedule(event_handler, "local_data_folder/", recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

## Backup e Recuperação

### Backup de Buckets

```bash
# Usando mc
mc cp --recursive datalab/bronze/ backup/bronze/
```

### Backup Agendado

Usando Prefect para backups agendados:

```python
from prefect import task, flow
from prefect.schedules import CronSchedule
import subprocess
import datetime

@task
def backup_bucket(bucket_name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"/backups/{bucket_name}_{timestamp}"
    
    result = subprocess.run([
        "mc", "cp", "--recursive", 
        f"datalab/{bucket_name}/", 
        backup_path
    ])
    
    return result.returncode == 0

@flow(schedule=CronSchedule("0 2 * * *"))  # Diariamente às 2h
def scheduled_backups():
    buckets = ["bronze", "silver", "gold"]
    results = {}
    
    for bucket in buckets:
        result = backup_bucket(bucket)
        results[bucket] = "Success" if result else "Failed"
    
    return results
```

## Melhores Práticas

1. **Organização**:
   - Use prefixos consistentes para organizar dados por domínio
   - Implemente convenções de nomenclatura claras
   - Armazene metadados junto com os dados

2. **Performance**:
   - Evite buckets com número excessivo de objetos (milhões+)
   - Utilize prefixos para melhor gerenciamento
   - Configure tamanhos apropriados de parte para uploads multipart

3. **Segurança**:
   - Implemente política de menor privilégio para acessos
   - Rotacione credenciais regularmente
   - Habilite criptografia em trânsito e em repouso

4. **Versionamento**:
   - Ative versionamento para buckets críticos
   - Configure políticas de ciclo de vida para versões antigas

5. **Monitoramento**:
   - Configure alertas para erros de acesso e capacidade
   - Monitore métricas de performance
   - Realize auditorias de acesso periodicamente

## Resolução de Problemas

| Problema              | Solução                                         |
| --------------------- | ----------------------------------------------- |
| Erro de acesso negado | Verifique credenciais e políticas de bucket     |
| Performance lenta     | Verifique tamanho de objetos, use compressão    |
| Conexão recusada      | Confirme que o serviço está rodando e acessível |
| Erro "NoSuchBucket"   | Verifique se o bucket existe e está acessível   |
| Objetos não listados  | Verifique prefixo correto e permissões          |

## Recursos Adicionais

- [Documentação Oficial do MinIO](https://docs.min.io/)
- [Cliente MinIO (mc)](https://docs.min.io/docs/minio-client-quickstart-guide.html)
- [Biblioteca Python para S3 (boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [Delta Lake com MinIO](https://docs.delta.io/latest/delta-storage.html)
- [Script de Inicialização MinIO](../../scripts/init_minio.sh)
