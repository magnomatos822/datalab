c = get_config()

# Configuração básica do JupyterHub
c.JupyterHub.ip = "0.0.0.0"
c.JupyterHub.port = 8888
c.JupyterHub.admin_access = True

# Autenticador simples para desenvolvimento
c.JupyterHub.authenticator_class = "jupyterhub.auth.DummyAuthenticator"
c.DummyAuthenticator.password = "datalab"

# Definir nomes de usuários permitidos
c.Authenticator.allowed_users = {"magnomatos822", "admin"}
c.Authenticator.admin_users = {"admin"}

# Configurar o inicializador do notebook
c.JupyterHub.spawner_class = "jupyterhub.spawner.SimpleLocalProcessSpawner"

# Configurar caminhos do usuário
c.Spawner.notebook_dir = "/home/jovyan/notebooks"
c.Spawner.default_url = "/lab"


# Configurar volumes persistentes
# Cada usuário terá seu próprio espaço de trabalho persistente
def create_dir_hook(spawner):
    username = spawner.user.name
    volume_path = f"/data/{username}"
    if not os.path.exists(volume_path):
        os.makedirs(volume_path, 0o755)
    spawner.notebook_dir = volume_path


c.Spawner.pre_spawn_hook = create_dir_hook

# Configuração de recursos
c.Spawner.mem_limit = "2G"
c.Spawner.cpu_limit = 2

# Configurar tempo de inatividade para economia de recursos
c.JupyterHub.last_activity_interval = 300
c.JupyterHub.activity_resolution = 60

# Configurar servidor para desligar quando inativo
c.JupyterHub.services = [
    {
        "name": "idle-culler",
        "command": [sys.executable, "-m", "jupyterhub_idle_culler", "--timeout=3600"],
        "admin": True,
    }
]

# Configuração de proxy
c.ConfigurableHTTPProxy.command = ["configurable-http-proxy"]
c.ConfigurableHTTPProxy.auth_token = "super-secret-token"
c.ConfigurableHTTPProxy.api_url = "http://localhost:8001"
