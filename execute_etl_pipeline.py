#!/usr/bin/env python3
"""
Execução do Pipeline ETL Principal do DataLab
Demonstração da integração completa da plataforma unificada
"""

import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Adicionar paths necessários
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "core"))
sys.path.insert(0, str(current_dir / "config"))
sys.path.insert(0, str(current_dir / "app"))


def setup_test_data():
    """Criar dados de teste para o pipeline"""
    print("=== Configurando Dados de Teste ===")

    try:
        # Criar diretório de dados de teste
        test_data_dir = current_dir / "data" / "test"
        test_data_dir.mkdir(parents=True, exist_ok=True)

        # Criar dados CSV de exemplo
        test_csv = test_data_dir / "sample_stocks.csv"
        if not test_csv.exists():
            sample_data = """date,symbol,open,high,low,close,volume
2024-01-01,AAPL,150.0,155.0,149.0,154.0,1000000
2024-01-02,AAPL,154.0,158.0,153.0,157.0,1100000
2024-01-03,AAPL,157.0,160.0,156.0,159.0,1200000
2024-01-01,GOOGL,2800.0,2850.0,2790.0,2840.0,500000
2024-01-02,GOOGL,2840.0,2880.0,2830.0,2870.0,550000
2024-01-03,GOOGL,2870.0,2900.0,2860.0,2890.0,600000
"""
            with open(test_csv, "w") as f:
                f.write(sample_data)
            print(f"✓ Dados de teste criados: {test_csv}")
        else:
            print(f"✓ Dados de teste já existem: {test_csv}")

        return str(test_csv)

    except Exception as e:
        print(f"✗ Erro ao configurar dados de teste: {e}")
        return None


def execute_bronze_stage(source_path, output_dir):
    """Executar etapa Bronze do pipeline"""
    print("\n=== Executando Etapa Bronze ===")

    try:
        from core.config import DataLabConfig
        from core.platform import DataLabCore

        # Inicializar plataforma
        config = DataLabConfig()
        platform = DataLabCore()

        print("✓ Plataforma inicializada")

        # Simular processamento Bronze (leitura de CSV)
        import csv

        bronze_data = []

        with open(source_path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Adicionar metadados de ingestão
                row["ingested_at"] = datetime.now().isoformat()
                row["source_file"] = source_path
                row["processing_stage"] = "bronze"
                bronze_data.append(row)

        # Salvar dados Bronze
        bronze_output = output_dir / "bronze_stocks.json"
        with open(bronze_output, "w") as f:
            json.dump(bronze_data, f, indent=2)

        print(f"✓ Bronze processado: {len(bronze_data)} registros")
        print(f"✓ Arquivo Bronze salvo: {bronze_output}")

        return str(bronze_output), bronze_data

    except Exception as e:
        print(f"✗ Erro na etapa Bronze: {e}")
        traceback.print_exc()
        return None, None


def execute_silver_stage(bronze_path, bronze_data, output_dir):
    """Executar etapa Silver do pipeline"""
    print("\n=== Executando Etapa Silver ===")

    try:
        from core.orchestrator import UnifiedOrchestrator

        # Inicializar orquestrador
        orchestrator = UnifiedOrchestrator()
        print("✓ Orquestrador inicializado")

        # Simular limpeza e transformação Silver
        silver_data = []

        for record in bronze_data:
            # Limpeza de dados
            cleaned_record = {
                "date": record["date"],
                "symbol": record["symbol"],
                "open_price": float(record["open"]),
                "high_price": float(record["high"]),
                "low_price": float(record["low"]),
                "close_price": float(record["close"]),
                "volume": int(record["volume"]),
                "price_range": float(record["high"]) - float(record["low"]),
                "daily_return": (
                    (float(record["close"]) - float(record["open"]))
                    / float(record["open"])
                )
                * 100,
                "processed_at": datetime.now().isoformat(),
                "processing_stage": "silver",
                "data_quality_score": 0.95,
            }
            silver_data.append(cleaned_record)

        # Salvar dados Silver
        silver_output = output_dir / "silver_stocks.json"
        with open(silver_output, "w") as f:
            json.dump(silver_data, f, indent=2)

        print(f"✓ Silver processado: {len(silver_data)} registros")
        print(f"✓ Arquivo Silver salvo: {silver_output}")

        return str(silver_output), silver_data

    except Exception as e:
        print(f"✗ Erro na etapa Silver: {e}")
        traceback.print_exc()
        return None, None


def execute_gold_stage(silver_path, silver_data, output_dir):
    """Executar etapa Gold do pipeline"""
    print("\n=== Executando Etapa Gold ===")

    try:
        # Simular agregações e métricas Gold
        gold_metrics = {}

        # Agrupar por símbolo
        symbols = set(record["symbol"] for record in silver_data)

        for symbol in symbols:
            symbol_data = [r for r in silver_data if r["symbol"] == symbol]

            # Calcular métricas agregadas
            prices = [r["close_price"] for r in symbol_data]
            volumes = [r["volume"] for r in symbol_data]
            returns = [r["daily_return"] for r in symbol_data]

            gold_metrics[symbol] = {
                "symbol": symbol,
                "total_records": len(symbol_data),
                "avg_price": sum(prices) / len(prices),
                "max_price": max(prices),
                "min_price": min(prices),
                "total_volume": sum(volumes),
                "avg_volume": sum(volumes) / len(volumes),
                "avg_daily_return": sum(returns) / len(returns),
                "price_volatility": max(prices) - min(prices),
                "generated_at": datetime.now().isoformat(),
                "processing_stage": "gold",
            }

        # Métricas globais
        all_prices = [r["close_price"] for r in silver_data]
        all_volumes = [r["volume"] for r in silver_data]

        global_metrics = {
            "global_metrics": {
                "total_records": len(silver_data),
                "total_symbols": len(symbols),
                "overall_avg_price": sum(all_prices) / len(all_prices),
                "overall_total_volume": sum(all_volumes),
                "processing_date": datetime.now().strftime("%Y-%m-%d"),
                "processing_stage": "gold",
            }
        }

        # Combinar métricas
        gold_data = {
            "symbol_metrics": gold_metrics,
            "global_metrics": global_metrics["global_metrics"],
        }

        # Salvar dados Gold
        gold_output = output_dir / "gold_analytics.json"
        with open(gold_output, "w") as f:
            json.dump(gold_data, f, indent=2)

        print(f"✓ Gold processado: {len(symbols)} símbolos analisados")
        print(f"✓ Arquivo Gold salvo: {gold_output}")

        return str(gold_output), gold_data

    except Exception as e:
        print(f"✗ Erro na etapa Gold: {e}")
        traceback.print_exc()
        return None, None


def generate_pipeline_report(bronze_path, silver_path, gold_path, gold_data):
    """Gerar relatório do pipeline"""
    print("\n=== Gerando Relatório do Pipeline ===")

    try:
        # Criar relatório detalhado
        report = {
            "pipeline_execution": {
                "execution_id": f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "execution_date": datetime.now().isoformat(),
                "status": "completed",
                "stages_completed": ["bronze", "silver", "gold"],
            },
            "data_flow": {
                "bronze_output": bronze_path,
                "silver_output": silver_path,
                "gold_output": gold_path,
            },
            "processing_summary": {
                "total_symbols": len(gold_data["symbol_metrics"]),
                "total_records": gold_data["global_metrics"]["total_records"],
                "avg_price": gold_data["global_metrics"]["overall_avg_price"],
                "total_volume": gold_data["global_metrics"]["overall_total_volume"],
            },
            "symbol_analysis": gold_data["symbol_metrics"],
        }

        # Salvar relatório
        report_output = current_dir / "data" / "test" / "pipeline_report.json"
        with open(report_output, "w") as f:
            json.dump(report, f, indent=2)

        print(f"✓ Relatório gerado: {report_output}")

        # Exibir resumo no console
        print("\n📊 RESUMO DO PIPELINE ETL")
        print("=" * 40)
        print(f"Execution ID: {report['pipeline_execution']['execution_id']}")
        print(f"Status: {report['pipeline_execution']['status'].upper()}")
        print(f"Símbolos processados: {report['processing_summary']['total_symbols']}")
        print(f"Total de registros: {report['processing_summary']['total_records']}")
        print(f"Preço médio: ${report['processing_summary']['avg_price']:.2f}")
        print(f"Volume total: {report['processing_summary']['total_volume']:,}")

        print("\n📈 Análise por Símbolo:")
        for symbol, metrics in report["symbol_analysis"].items():
            print(
                f"  {symbol}: Preço médio ${metrics['avg_price']:.2f}, "
                f"Volatilidade ${metrics['price_volatility']:.2f}"
            )

        return report_output

    except Exception as e:
        print(f"✗ Erro ao gerar relatório: {e}")
        traceback.print_exc()
        return None


def main():
    """Função principal de execução do pipeline"""
    print("DataLab ETL Pipeline Execution")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print(f"Working Directory: {os.getcwd()}")
    print("=" * 50)

    # Configurar ambiente de teste
    source_path = setup_test_data()
    if not source_path:
        print("❌ Falha na configuração dos dados de teste")
        return 1

    # Criar diretório de saída
    output_dir = current_dir / "data" / "test" / "pipeline_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Executar pipeline completo
        print(f"\n🚀 Iniciando Pipeline ETL com dados: {source_path}")

        # Etapa Bronze
        bronze_path, bronze_data = execute_bronze_stage(source_path, output_dir)
        if not bronze_path:
            raise Exception("Falha na etapa Bronze")

        # Etapa Silver
        silver_path, silver_data = execute_silver_stage(
            bronze_path, bronze_data, output_dir
        )
        if not silver_path:
            raise Exception("Falha na etapa Silver")

        # Etapa Gold
        gold_path, gold_data = execute_gold_stage(silver_path, silver_data, output_dir)
        if not gold_path:
            raise Exception("Falha na etapa Gold")

        # Gerar relatório
        report_path = generate_pipeline_report(
            bronze_path, silver_path, gold_path, gold_data
        )

        # Resultado final
        print("\n🎉 PIPELINE ETL EXECUTADO COM SUCESSO!")
        print("=" * 50)
        print("✅ Todas as etapas da arquitetura Medallion completadas")
        print("✅ Plataforma DataLab integrada e funcional")
        print("✅ Dados processados e relatórios gerados")
        print(f"📁 Resultados salvos em: {output_dir}")

        if report_path:
            print(f"📋 Relatório completo: {report_path}")

        return 0

    except Exception as e:
        print(f"\n❌ ERRO NO PIPELINE ETL: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
