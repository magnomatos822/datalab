#!/usr/bin/env python3
"""
Script de teste da integração da plataforma DataLab
Testa todos os componentes principais sem dependências externas
"""

import os
import sys

sys.path.append(".")


def test_core_platform():
    """Testa o núcleo da plataforma"""
    print("🔍 Testando núcleo da plataforma...")

    try:
        from core.platform import DataLabCore

        platform = DataLabCore()
        print(f"✅ DataLabCore inicializada")
        print(f"   📊 Serviços: {len(platform.services)}")
        print(f"   🔄 Pipelines: {len(platform.pipelines)}")
        print(f"   ⚙️ Versão: {platform.config.get('version', 'N/A')}")
        return platform
    except Exception as e:
        print(f"❌ Erro no core platform: {e}")
        return None


def test_config_manager():
    """Testa o gerenciador de configuração"""
    print("\n🔍 Testando gerenciador de configuração...")

    try:
        from core.config import DataLabConfig

        config_manager = DataLabConfig()
        print(f"✅ DataLabConfig inicializado")

        # Testar algumas operações básicas
        config = config_manager.get_config_value("platform.version", "N/A")
        print(f"   📋 Config platform.version: {config}")

        # Testar config de serviço
        try:
            spark_config = config_manager.get_service_config("spark")
            print(f"   ⚡ Config Spark carregada: {bool(spark_config)}")
        except Exception as e:
            print(f"   ⚠️ Spark config não disponível: {e}")

        return config_manager
    except Exception as e:
        print(f"❌ Erro no config manager: {e}")
        return None


def test_orchestrator():
    """Testa o orquestrador unificado"""
    print("\n🔍 Testando orquestrador unificado...")

    try:
        from core.orchestrator import UnifiedOrchestrator

        orchestrator = UnifiedOrchestrator()
        print(f"✅ UnifiedOrchestrator inicializado")
        print(f"   🔄 Pipelines registrados: {len(orchestrator.registered_pipelines)}")
        print(f"   📋 Tasks registradas: {len(getattr(orchestrator, 'tasks', {}))}")
        return orchestrator
    except Exception as e:
        print(f"❌ Erro no orchestrator: {e}")
        return None


def test_platform_integration(platform, config_manager, orchestrator):
    """Testa integração entre componentes"""
    print("\n🔍 Testando integração da plataforma...")

    if not all([platform, config_manager, orchestrator]):
        print("⚠️ Nem todos os componentes estão disponíveis para teste de integração")
        return False

    try:
        # Testar obtenção de métricas
        metrics = platform.get_unified_metrics()
        print(f"✅ Métricas unificadas: {len(metrics)} categorias")

        # Testar status da plataforma
        status = platform.get_platform_status()
        print(f"✅ Status da plataforma: {status.get('status', 'unknown')}")

        # Testar configuração
        spark_config = config_manager.get_config_value("spark.enabled", False)
        print(f"✅ Config Spark enabled: {spark_config}")

        return True
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        return False


def test_cli_compatibility():
    """Testa compatibilidade com CLI"""
    print("\n🔍 Testando compatibilidade com CLI...")

    try:
        # Testar se o CLI pode importar os módulos
        import datalab_cli

        print("✅ CLI pode ser importada")

        # Testar se o manager pode ser importado
        import datalab_manager

        print("✅ Manager pode ser importado")

        return True
    except Exception as e:
        print(f"❌ Erro na compatibilidade CLI: {e}")
        return False


def main():
    """Função principal do teste"""
    print("🚀 DataLab Platform Integration Test")
    print("=" * 50)

    # Testes individuais
    platform = test_core_platform()
    config_manager = test_config_manager()
    orchestrator = test_orchestrator()

    # Teste de integração
    integration_ok = test_platform_integration(platform, config_manager, orchestrator)

    # Teste de compatibilidade
    cli_ok = test_cli_compatibility()

    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)

    components = [
        ("Core Platform", platform is not None),
        ("Config Manager", config_manager is not None),
        ("Orchestrator", orchestrator is not None),
        ("Integração", integration_ok),
        ("CLI Compatibility", cli_ok),
    ]

    passed = sum(1 for _, status in components if status)
    total = len(components)

    for name, status in components:
        print(f"{'✅' if status else '❌'} {name}")

    print(f"\n📈 Taxa de sucesso: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print("⚠️ Alguns testes falharam")
        return 1


if __name__ == "__main__":
    exit(main())
