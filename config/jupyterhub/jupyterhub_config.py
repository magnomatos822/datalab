import os
import sys

c = get_config()

# Configuração básica do JupyterHub
c.JupyterHub.ip = "0.0.0.0"
c.JupyterHub.port = 8000
c.JupyterHub.admin_access = True

# Configuração para Docker - usar DummyAuthenticator para simplicidade
c.JupyterHub.authenticator_class = "jupyterhub.auth.DummyAuthenticator"

# Usuários permitidos
c.Authenticator.allowed_users = {"admin", "user1", "user2"}
c.Authenticator.admin_users = {"admin"}

# Configurar o spawner para Docker
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"

# Configuração do Docker Spawner
c.DockerSpawner.image = "jupyter/datascience-notebook:latest"
c.DockerSpawner.network_name = "datalab_dataflow-network"
c.DockerSpawner.remove = True  # Remove containers após o uso
c.DockerSpawner.debug = True

# Volumes compartilhados
c.DockerSpawner.volumes = {
    "/home/magnomatos/Documentos/projetos-pessoais/datalab/notebooks": "/home/jovyan/work",
}

# Configurações de recursos
c.DockerSpawner.mem_limit = "2G"
c.DockerSpawner.cpu_limit = 2.0

# Configurações de rede e comunicação
c.DockerSpawner.hub_connect_ip = "jupyter"  # Nome do serviço no Docker Compose
c.DockerSpawner.use_internal_ip = True

# Configuração do notebook
c.Spawner.default_url = "/lab"
c.Spawner.start_timeout = 120

# Configurações de log
c.JupyterHub.log_level = "INFO"

# Configurar tempo de inatividade
c.JupyterHub.last_activity_interval = 300
c.JupyterHub.activity_resolution = 60

# Configurar proxy
c.ConfigurableHTTPProxy.auth_token = "super-secret-token"

# Configuração de segurança para desenvolvimento
c.JupyterHub.allow_named_servers = True
c.JupyterHub.named_server_limit_per_user = 3
