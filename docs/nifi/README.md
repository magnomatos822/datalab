# Apache NiFi - Automação de Fluxos de Dados

<div align="center">
  <img src="https://img.shields.io/static/v1?style=for-the-badge&message=Apache+NiFi&color=728E9B&logo=Apache+NiFi&logoColor=FFFFFF&label=" alt="Apache NiFi">
</div>

> Versão: 2.4.0

## O que é Apache NiFi?

Apache NiFi é uma plataforma de integração de dados projetada para automatizar o fluxo de dados entre sistemas. Baseado no conceito de "dataflow programming", o NiFi oferece uma interface gráfica web para projetar, controlar e monitorar fluxos de dados, facilitando a ingestão, transformação, roteamento e distribuição de dados entre diferentes fontes e destinos.

No DataFlow Lab, o NiFi serve como ferramenta principal de ingestão de dados, alimentando a camada Bronze do Data Lakehouse com dados de diversas origens.

## Características Principais

- **Interface Visual**: Design de fluxos de dados através de interface gráfica drag-and-drop
- **Controle de Fluxo de Dados**: Transformações, roteamento, agregação e distribuição
- **Rastreabilidade**: Proveniência de dados para auditoria completa
- **Extensível**: Mais de 300 processadores para diferentes operações e integrações
- **Tolerante a Falhas**: Persistência de dados em situações de falha ou interrupção
- **Segurança**: Controle de acesso, SSL/TLS, e autenticação integrada

## Como Acessar

O Apache NiFi está disponível em:

- **URL**: [https://localhost:8443/nifi](https://localhost:8443/nifi)
- **Credenciais**:
  - Usuário: nifi
  - Senha: HGd15bvfv8744ghbdhgdv7895agqERAo

## Arquitetura do NiFi no DataFlow Lab

```
                  +-------------------+
                  |                   |
                  |   Apache NiFi     |
                  |   (8443)          |
                  |                   |
                  +-------------------+
                          |
                          |
          +---------------+---------------+
          |               |               |
+---------v----+  +-------v------+  +-----v--------+
|              |  |              |  |              |
|  Fontes de   |  |    MinIO     |  |   Outros    |
|    Dados     |  |  (Bronze)    |  |  Destinos   |
|              |  |              |  |              |
+--------------+  +--------------+  +--------------+
```

## Componentes no DataFlow Lab

O NiFi foi configurado no DataFlow Lab com:

1. **Container Docker Customizado**: Baseado na imagem oficial 2.4.0
2. **Drivers JDBC organizados**: Pré-instalados e organizados por tipo de banco
   - PostgreSQL (postgresql-42.6.0.jar)
   - MySQL
   - MS SQL Server
   - Oracle
3. **Volumes Persistentes**: Para configuração, estado e conteúdo
4. **Acesso Seguro**: Configurado com HTTPS
5. **Alta disponibilidade**: TZ configurada para América/Fortaleza

## Conceitos Básicos do NiFi

### 1. Processadores

Os processadores são os componentes fundamentais que executam ações sobre os dados:

- Obtenção de dados (GetFile, GetHTTP, ExecuteSQL)
- Transformação (ConvertRecord, ExecuteScript, JoltTransformJSON)
- Roteamento (RouteOnAttribute, RouteOnContent)
- Entrega (PutFile, PutS3Object, PublishKafka)

### 2. FlowFiles

FlowFiles são os objetos que contêm:

- **Conteúdo**: Os dados sendo processados
- **Atributos**: Metadados sobre os dados (nomes, timestamps, etc.)

### 3. Conexões

Conexões são os links entre processadores que controlam:

- Filas de FlowFiles
- Prioridade e backpressure
- Relacionamentos entre processadores

### 4. Process Groups

Agrupamentos lógicos de processadores e conexões para organizar fluxos complexos.

## Exemplos de Uso

### Exemplo 1: Ingestão de Arquivo para MinIO (Bronze Layer)

```
GetFile -> ExtractText -> UpdateAttribute -> PutS3Object
```

1. **GetFile**:
   - Diretório de entrada: `/caminho/para/dados`
   - Padrão de arquivo: `*.csv`
   - Batch size: 10

2. **ExtractText** (opcional, para extração de metadados):
   - Extrai informações do arquivo como timestamp ou cabeçalhos

3. **UpdateAttribute**:
   - Adiciona metadados de ingestão
   - Define caminho no bucket S3
   ```
   s3.bucket: bronze
   s3.key: raw_data_source1/table1/${filename}
   ingest.timestamp: ${now():format("yyyy-MM-dd'T'HH:mm:ss'Z'")}
   ingest.source: file_system
   ```

4. **PutS3Object**:
   - Endpoint Override: http://minio:9000
   - Access Key: admin
   - Secret Key: admin123
   - Bucket: ${s3.bucket}
   - Key: ${s3.key}

### Exemplo 2: Ingestão de Banco de Dados para Delta Lake

```
ExecuteSQL -> ConvertAvroToJSON -> UpdateAttribute -> PutFile -> ExecuteStreamCommand
```

1. **ExecuteSQL**:
   - Driver: org.postgresql.Driver
   - URL: jdbc:postgresql://postgres:5432/database
   - Query: SELECT * FROM tabela WHERE updated_at > ${last_execution:toNumber()}
   - Formato de saída: Avro

2. **ConvertAvroToJSON**:
   - Converte os registros Avro para JSON

3. **UpdateAttribute**:
   - filename: dados_${now():format("yyyyMMdd_HHmmss")}.json
   - target.dir: /tmp/delta_staging

4. **PutFile**:
   - Diretório: ${target.dir}
   - Conflito: Renomear

5. **ExecuteStreamCommand** (para salvar em formato Delta via Spark Submit):
   - Comando: /opt/spark/bin/spark-submit --master spark://spark-master:7077 /caminho/para/bronze_ingestion.py --input-path=${target.dir}/${filename} --output-path=s3a://bronze/raw_data_source2/table1/

### Exemplo 3: Monitoramento de API e Publicação em Kafka

```
InvokeHTTP -> SplitJSON -> EvaluateJsonPath -> RouteOnAttribute -> PublishKafka
```

1. **InvokeHTTP**:
   - URL: https://api.exemplo.com/dados
   - Método: GET
   - Agendamento: 5 min

2. **SplitJSON**:
   - JSONPath: $.items[*]
   - Dividir array em FlowFiles individuais

3. **EvaluateJsonPath**:
   - Extrai atributos do JSON:
   - event.type: $.type
   - event.id: $.id
   - event.value: $.value

4. **RouteOnAttribute**:
   - Rotas baseadas no tipo de evento:
   - ${event.type:equals("create")}: create
   - ${event.type:equals("update")}: update
   - ${event.type:equals("delete")}: delete

5. **PublishKafka_2_6**:
   - Kafka Brokers: kafka:9092
   - Tópico: data-events
   - Use Transactions: true

## Integração com Outros Componentes do DataFlow Lab

### 1. NiFi + MinIO

Para transferir dados para o armazenamento de objetos:

```
[Qualquer Source] -> PutS3Object
```

Configuração do PutS3Object:
- Endpoint Override: http://minio:9000
- Região: us-east-1
- Bucket: [bronze/silver/gold dependendo do caso]
- Credenciais: admin/admin123

### 2. NiFi + Spark/Delta Lake

Para iniciar processamento Spark:

```
[Fonte de dados] -> [Processamento] -> MergeContent -> ExecuteStreamCommand
```

Configuração do ExecuteStreamCommand:
```
Command: /opt/spark/bin/spark-submit
Arguments: --master spark://spark-master:7077 /opt/spark-apps/process_data.py --input-path=${absolute.path}
```

### 3. NiFi + Kafka

Para publicar mensagens no Kafka:

```
[Source] -> [Transformação] -> PublishKafka_2_6
```

Configuração do PublishKafka_2_6:
- Kafka Brokers: kafka:9092
- Topic Name: [nome do tópico]
- Key Attribute: [atributo a usar como chave]

### 4. NiFi + Prefect

Para acionar fluxos no Prefect:

```
[Trigger Condition] -> InvokeHTTP
```

Configuração do InvokeHTTP:
- URL: http://prefect:4200/api/flow_runs/
- Method: POST
- Content-Type: application/json
- Request Body: {"flow_id": "${flow.id}"}

## Templates e Fluxos Comuns

### Template 1: Ingestão da Camada Bronze

Template para ingestão padronizada na camada Bronze com gestão de metadados:

1. Obter dados da fonte
2. Extrair ou adicionar metadados (fonte, timestamp, versão)
3. Adicionar dados na estrutura Bronze no MinIO
4. Registrar metadata no catálogo (opcional)

### Template 2: Processamento CDC (Change Data Capture)

Template para detecção e captura de mudanças:

1. Verificar timestamp da última execução
2. Consultar dados alterados desde então
3. Converter para formato padronizado
4. Enviar para camada Bronze com metadados de operação (insert/update/delete)

### Template 3: Validação e Controle de Qualidade

Template para validação de dados antes da ingestão:

1. Obter dados da fonte
2. Aplicar regras de validação 
3. Separar registros válidos e inválidos
4. Enriquecer com informações de qualidade
5. Armazenar válidos no fluxo principal
6. Armazenar inválidos em área de quarentena

## Melhores Práticas

### 1. Organização

- **Use Process Groups**: Organize fluxos por fonte, destino ou caso de uso
- **Nomeie processadores claramente**: Inclua propósito e parâmetros importantes
- **Adicione comentários/rótulos**: Documente decisões e requisitos

### 2. Performance

- **Ajuste batch sizes**: Encontre o equilíbrio entre latência e throughput
- **Use backpressure**: Configure limites de filas para evitar sobrecargas
- **Monitore uso de recursos**: CPU, memória, E/S de disco

### 3. Segurança e Confiabilidade

- **Mascare dados sensíveis**: Use ReplaceText para ocultar informações sensíveis
- **Configure retry**: Adicione políticas de retry para conexões externas instáveis
- **Use funções de controle de fluxo**: Wait, Monitoring para regular o fluxo

### 4. Monitoramento

- **Habilite proveniência de dados**: Para auditoria e resolução de problemas
- **Configure notificações**: UseNotify, Email para alertas automáticos
- **Implemente Circuit Breakers**: Para proteger sistemas downstream

### 5. Gestão de Dados

- **Estabeleça convenções de nomeação**: Para buckets e caminhos no MinIO
- **Adicione metadados padronizados**: Source, ingest_time, version, etc.
- **Versione seus templates**: Para facilitar rollbacks e documentação

## Drivers JDBC Incluídos

O Docker do NiFi inclui os seguintes drivers JDBC:

| Banco de Dados       | Driver                       | Localização                              |
| -------------------- | ---------------------------- | ---------------------------------------- |
| PostgreSQL           | postgresql-42.6.0.jar        | /opt/nifi/nifi-current/drivers/postgres/ |
| MySQL                | mysql-connector-j-8.0.33.jar | /opt/nifi/nifi-current/drivers/mysql/    |
| Microsoft SQL Server | mssql-jdbc-12.2.0.jre11.jar  | /opt/nifi/nifi-current/drivers/mssql/    |
| Oracle               | ojdbc11-23.2.0.0.jar         | /opt/nifi/nifi-current/drivers/oracle/   |

## Resolução de Problemas

| Problema                       | Possível Solução                                            |
| ------------------------------ | ----------------------------------------------------------- |
| Processador preso em "Stopped" | Verifique logs do processador; reinicie o processador       |
| Falhas de conexão com MinIO    | Verifique credenciais e se MinIO está acessível             |
| Erros de memória               | Aumente a memória do container ou ajuste concurrent tasks   |
| SQL Timeout                    | Ajuste timeout na configuração do banco ou divida consultas |
| FlowFiles presos em filas      | Verifique a configuração do relacionamento de saída         |
| NiFi UI inacessível            | Verifique logs do container: `docker logs apache-nifi`      |

## Recursos Adicionais

- [Documentação Oficial do Apache NiFi](https://nifi.apache.org/docs.html)
- [Best Practices NiFi](https://nifi.apache.org/docs/nifi-docs/html/best-practices.html)
- [Template Gallery](https://cwiki.apache.org/confluence/display/NIFI/Example+Dataflow+Templates)
- [NiFi Expression Language Guide](https://nifi.apache.org/docs/nifi-docs/html/expression-language-guide.html)
- [NiFi Records and Schemas](https://nifi.apache.org/docs/nifi-docs/html/record-path-guide.html)