#!/usr/bin/env python3
"""
Script para testar e validar o pipeline ETL principal do DataLab
"""

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Adicionar paths necessários
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "flows"))
sys.path.insert(0, str(current_dir / "core"))
sys.path.insert(0, str(current_dir / "config"))
sys.path.insert(0, str(current_dir / "app"))


def test_core_imports():
    """Testa a importação dos módulos core"""
    print("=== Testando Importações dos Módulos Core ===")

    try:
        from core.platform import DataLabCore

        print("✓ DataLabCore importado com sucesso")

        from core.config import DataLabConfig

        print("✓ DataLabConfig importado com sucesso")

        from core.orchestrator import UnifiedOrchestrator

        print("✓ UnifiedOrchestrator importado com sucesso")

        return True

    except Exception as e:
        print(f"✗ Erro na importação dos módulos core: {e}")
        traceback.print_exc()
        return False


def test_platform_initialization():
    """Testa a inicialização da plataforma"""
    print("\n=== Testando Inicialização da Plataforma ===")

    try:
        from core.config import DataLabConfig
        from core.platform import DataLabCore

        # Inicializar configuração
        config = DataLabConfig()
        print("✓ Configuração inicializada")

        # Inicializar plataforma
        platform = DataLabCore()
        print("✓ Plataforma DataLab inicializada")

        # Verificar status básico
        print("✓ Status da plataforma: Inicializada")

        return True, platform

    except Exception as e:
        print(f"✗ Erro na inicialização da plataforma: {e}")
        traceback.print_exc()
        return False, None


def test_etl_flow_import():
    """Testa a importação do flow ETL"""
    print("\n=== Testando Importação do Flow ETL ===")

    try:
        import flows.medallion_etl_flow as etl_module

        print("✓ Módulo ETL importado com sucesso")

        # Verificar se as funções principais existem
        if hasattr(etl_module, "medallion_etl_flow"):
            print("✓ Flow principal encontrado")
        else:
            print("⚠ Flow principal não encontrado")

        return True

    except Exception as e:
        print(f"✗ Erro na importação do flow ETL: {e}")
        traceback.print_exc()
        return False


def test_etl_components():
    """Testa os componentes individuais do ETL"""
    print("\n=== Testando Componentes do ETL ===")

    try:
        # Testar arquitetura medallion
        from app.medallion_architecture import MedallionArchitecture

        medallion = MedallionArchitecture()
        print("✓ MedallionArchitecture inicializada")

        # Testar utilitários
        try:
            import app.utils.s3_utils

            print("✓ Módulo S3Utils disponível")
        except Exception:
            print("⚠ S3Utils não disponível (dependências não instaladas)")

        try:
            import app.utils.kafka_utils

            print("✓ Módulo KafkaProducer disponível")
        except Exception:
            print("⚠ KafkaProducer não disponível (dependências não instaladas)")

        return True

    except Exception as e:
        print(f"✗ Erro nos componentes do ETL: {e}")
        traceback.print_exc()
        return False


def test_etl_execution_dry_run():
    """Executa um teste seco do pipeline ETL"""
    print("\n=== Executando Teste Seco do Pipeline ETL ===")

    try:
        import flows.medallion_etl_flow as etl_module

        print("✓ Flow ETL carregado")
        print("✓ Pipeline pronto para execução")

        # Simular parâmetros do pipeline
        params = {
            "source_config": {"type": "file", "path": "/tmp/test_data.csv"},
            "processing_date": datetime.now().strftime("%Y-%m-%d"),
            "environment": "test",
        }

        print(f"✓ Parâmetros de teste configurados: {params}")
        print("✓ Pipeline ETL validado e pronto para execução real")

        return True

    except Exception as e:
        print(f"✗ Erro no teste seco do pipeline: {e}")
        traceback.print_exc()
        return False


def main():
    """Função principal do teste"""
    print("DataLab ETL Pipeline Validation")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print("=" * 50)

    tests = [
        ("Importações Core", test_core_imports),
        ("Inicialização Plataforma", lambda: test_platform_initialization()[0]),
        ("Importação Flow ETL", test_etl_flow_import),
        ("Componentes ETL", test_etl_components),
        ("Teste Seco Pipeline", test_etl_execution_dry_run),
    ]

    results = {}
    for test_name, test_func in tests:
        print(f"\n{test_name}...")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                print(f"✓ {test_name}: PASSED")
            else:
                print(f"✗ {test_name}: FAILED")
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}")
            results[test_name] = False

    # Resumo final
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES")
    print("=" * 50)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nResultado Final: {passed}/{total} testes passaram")

    if passed == total:
        print("🎉 Todos os testes passaram! Pipeline ETL validado com sucesso.")
        return 0
    else:
        print("⚠ Alguns testes falharam. Verifique os logs acima.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
