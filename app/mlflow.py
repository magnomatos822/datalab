"""
Arquivo de redirecionamento para app.py.
Este arquivo existe apenas para resolver um problema onde algum componente
está tentando executar '/app/mlflow' em vez de executar o app.py diretamente.
"""

import importlib.util
import sys

# Carrega o módulo app.py
spec = importlib.util.spec_from_file_location("app", "app.py")
app = importlib.util.module_from_spec(spec)
sys.modules["app"] = app
spec.loader.exec_module(app)

# O código acima essencialmente importa e executa app.py
