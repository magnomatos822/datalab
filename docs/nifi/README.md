# Apache NiFi no DataLab

## Visão Geral
O Apache NiFi 2.4.0 é uma plataforma poderosa para automação e gerenciamento de fluxos de dados entre sistemas. Projetado para automação de fluxos de dados entre sistemas, o NiFi suporta processamento e distribuição de dados em tempo real.

## Acesso
- **URL**: https://localhost:8443/nifi
- **Usuário**: admin
- **Senha**: admin123

## Novidades na Versão 2.4.0
- Melhor desempenho e escalabilidade
- Interface de usuário aprimorada
- Novos processadores e controladores
- Suporte aprimorado para contêineres
- Maior segurança e estabilidade

## Configuração
O NiFi está configurado para trabalhar com outros componentes do DataLab:
- Conexão com MinIO para armazenamento de dados
- Integração com o Apache Spark para processamento de dados em lote ou streaming
- Possibilidade de acionar fluxos do Prefect

## Casos de Uso
- Ingestão de dados em lote ou streaming para o Data Lake (MinIO)
- Transformações leves e roteamento de dados
- Orquestração de processos e workflows de dados
- Monitoramento e alerta de fluxos de dados

## Arquitetura de Integração
O NiFi pode ser usado como componente central de ingestão na arquitetura Medallion:
1. **Bronze**: Ingestão de dados brutos através do NiFi para o MinIO
2. **Silver**: Acionamento de jobs Spark para limpeza e transformação
3. **Gold**: Preparação final dos dados para análise e consumo

## Primeiros Passos
1. Acesse a interface web do NiFi em https://localhost:8443/nifi
2. Faça login com as credenciais padrão
3. Crie seu primeiro fluxo arrastando e soltando processadores na tela
4. Configure processadores para se conectar ao MinIO ou outros serviços

## Dicas de Segurança
- Altere a senha padrão do administrador em ambiente de produção
- Configure SSL adequadamente para ambientes não locais
- Utilize variáveis sensíveis para armazenar credenciais