# 🚀 DataLab - Ambiente Completo de Data Science

Este é o **docker-compose principal** que orquestra todo o ambiente DataLab, combinando todos os módulos em um único stack integrado.

## 📋 Visão Geral

O DataLab é uma plataforma completa de Data Science que inclui:

- **🗄️ Armazenamento**: MinIO (S3-compatible)
- **🔄 Streaming**: Apache Kafka
- **⚡ Processamento**: Apache Spark (Master + Workers)
- **🤖 ML Lifecycle**: MLflow
- **🔀 Orquestração**: Prefect
- **📊 Análise**: JupyterHub
- **🖥️ Visualização**: Streamlit
- **📈 Monitoramento**: Prometheus + Grafana

## 🎯 Início Rápido

### Pré-requisitos

- Docker >= 20.10
- Docker Compose >= 2.0
- 8GB+ de RAM disponível
- 20GB+ de espaço em disco

### Instalação Simples

```bash
# 1. Clone ou acesse o diretório do projeto
cd /home/magnomatos/Documentos/projetos-pessoais/datalab

# 2. Inicie todo o ambiente
./manage.sh start

# 3. Acesse os serviços (URLs listadas após inicialização)
```

## 🛠️ Script de Gerenciamento

O script `manage.sh` facilita o controle do ambiente:

```bash
# Iniciar todos os serviços
./manage.sh start

# Iniciar apenas serviços específicos
./manage.sh start core          # MinIO + Kafka
./manage.sh start processing    # Spark
./manage.sh start ml           # MLflow + Prefect
./manage.sh start visualization # Jupyter + Streamlit
./manage.sh start monitoring   # Prometheus + Grafana

# Parar serviços
./manage.sh stop
./manage.sh stop ml

# Verificar status
./manage.sh status

# Ver logs
./manage.sh logs
./manage.sh logs mlflow

# Verificar saúde dos serviços
./manage.sh health

# Mostrar URLs de acesso
./manage.sh urls

# Limpeza completa
./manage.sh clean

# Ajuda
./manage.sh help
```

## 🌐 URLs de Acesso

Após inicializar, os serviços estarão disponíveis em:

| Serviço           | URL                   | Credenciais      |
| ----------------- | --------------------- | ---------------- |
| **MinIO Console** | http://localhost:9001 | admin / admin123 |
| **Spark Master**  | http://localhost:8080 | -                |
| **MLflow**        | http://localhost:5000 | -                |
| **Prefect**       | http://localhost:4200 | -                |
| **JupyterHub**    | http://localhost:8888 | -                |
| **Streamlit**     | http://localhost:8501 | -                |
| **Prometheus**    | http://localhost:9090 | -                |
| **Grafana**       | http://localhost:3000 | admin / admin    |

## 🏗️ Arquitetura

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   MinIO     │  │    Kafka    │  │    Spark    │
│  (Storage)  │  │ (Streaming) │  │(Processing) │
└─────────────┘  └─────────────┘  └─────────────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   MLflow    │  │   Prefect   │  │  Jupyter    │
│    (ML)     │  │(Workflows)  │  │ (Analysis)  │
└─────────────┘  └─────────────┘  └─────────────┘
        │                               │
        └───────────────┬───────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌─────────────┐              ┌─────────────┐
│ Prometheus  │              │  Streamlit  │
│(Monitoring) │              │   (Apps)    │
└─────────────┘              └─────────────┘
        │
┌─────────────┐
│   Grafana   │
│(Dashboard)  │
└─────────────┘
```

## 🔧 Configuração

### Variáveis de Ambiente

As principais variáveis estão no arquivo `.env`:

```bash
# Credenciais MinIO/S3
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=admin123
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin

# URLs dos serviços
MLFLOW_TRACKING_URI=http://mlflow:5000
S3_ENDPOINT=http://minio:9000
```

### Recursos Recomendados

| Perfil          | CPU       | RAM   | Descrição         |
| --------------- | --------- | ----- | ----------------- |
| **Mínimo**      | 4 cores   | 8GB   | Core + ML básico  |
| **Recomendado** | 8 cores   | 16GB  | Ambiente completo |
| **Produção**    | 16+ cores | 32GB+ | Alta performance  |

## 📁 Estrutura de Dados

O MinIO organiza os dados seguindo a **Arquitetura Medallion**:

```
minio/
├── bronze/     # Dados brutos
├── silver/     # Dados limpos
├── gold/       # Dados analíticos
├── mlflow/     # Artefatos ML
├── jupyter/    # Notebooks
└── prefect/    # Workflows
```

## 🔧 Desenvolvimento

### Adicionando Novos Serviços

1. Edite o `docker-compose.yml`
2. Adicione o serviço na rede `dataflow-network`
3. Configure volumes e variáveis de ambiente
4. Atualize o script `manage.sh` se necessário

### Volumes Persistentes

Os dados são mantidos em volumes Docker:

```bash
# Listar volumes
docker volume ls | grep datalab

# Backup de volume específico
docker run --rm -v datalab_minio-data:/data -v $(pwd):/backup ubuntu tar czf /backup/minio-backup.tar.gz -C /data .
```

## 🚨 Troubleshooting

### Problemas Comuns

**Porta já em uso:**
```bash
# Verificar portas em uso
sudo netstat -tulpn | grep :9000

# Parar serviços conflitantes
sudo systemctl stop apache2  # exemplo
```

**Pouco espaço em disco:**
```bash
# Limpar imagens não utilizadas
docker system prune -a

# Verificar uso de espaço
docker system df
```

**Serviços não respondem:**
```bash
# Verificar logs
./manage.sh logs [nome-do-serviço]

# Verificar saúde
./manage.sh health

# Reiniciar serviço específico
docker-compose restart [nome-do-serviço]
```

### Logs e Debugging

```bash
# Logs em tempo real
./manage.sh logs

# Logs de serviço específico
./manage.sh logs mlflow

# Debug de rede
docker network inspect datalab_dataflow-network
```

## 🔒 Segurança

### Configurações de Produção

Para ambientes de produção, altere:

1. **Senhas padrão** no arquivo `.env`
2. **Certificados SSL** para HTTPS
3. **Autenticação** no JupyterHub
4. **Firewall** para portas expostas

```bash
# Gerar senhas seguras
openssl rand -base64 32
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

- 📧 Email: [seu-email@exemplo.com]
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/datalab/issues)
- 📖 Docs: [Documentação Completa](./docs/)

---

⭐ **Se este projeto foi útil, deixe uma estrela!** ⭐
