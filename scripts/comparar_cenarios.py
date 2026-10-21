"""Compara o cenário sem otimização com o cenário com otimização (README, seção 5.4).

Os dois cenários usam a mesma semente, então veem o mesmo clima e a mesma carga.
A simulação começa às 07:00 do dia inicial e termina às 07:00 do dia seguinte ao último,
para fechar o último ciclo de carga noturna do carro.

Uso: python scripts/comparar_cenarios.py [--dias 7] [--inicio 2026-01-05] [--semente 42]
         [--clima "ensolarado,chuvoso"] [--valor-exportacao 0.0] [--fator-co2 KG_POR_KWH]
         [--sem-marketplace] [--json dados/processados/comparison.json] [--simulacao demo]
"""
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simulator.scenario import run  # noqa: E402

DEFAULT_WEATHER = "ensolarado,ensolarado,parcialmente nublado,chuvoso,ensolarado,parcialmente nublado,ensolarado"


def totals(metrics):
    return {
        "import_kwh": sum(m.import_kwh for m in metrics.values()),
        "export_kwh": sum(m.export_kwh for m in metrics.values()),
        "cost": sum(m.cost for m in metrics.values()),
        "market_sold_kwh": sum(m.market_sold_kwh for m in metrics.values()),
        "market_gain": sum(m.market_gain for m in metrics.values()),
        "visits": sum(m.visits for m in metrics.values()),
        "visits_on_target": sum(m.visits_on_target for m in metrics.values()),
    }


def print_scenario(title, metrics, co2_factor):
    print(f"\n{title}")
    header = (f"{'casa':<9}{'importado kWh':>14}{'exportado kWh':>14}{'autoconsumo %':>14}"
              f"{'vendido kWh':>12}{'comprado kWh':>13}{'ganho mkt R$':>13}{'custo R$':>10}{'carro no alvo':>15}")
    print(header + (f"{'CO2 kg':>9}" if co2_factor is not None else ""))
    for house_id, m in metrics.items():
        target = f"{m.visits_on_target}/{m.visits}" if m.visits else "-"
        line = (f"{house_id:<9}{m.import_kwh:>14.1f}{m.export_kwh:>14.1f}"
                f"{m.self_consumption_percent:>14.1f}{m.market_sold_kwh:>12.1f}{m.market_bought_kwh:>13.1f}"
                f"{m.market_gain:>13.2f}{m.cost:>10.2f}{target:>15}")
        if co2_factor is not None:
            line += f"{m.import_kwh * co2_factor:>9.2f}"
        print(line)
    t = totals(metrics)
    bought = sum(m.market_bought_kwh for m in metrics.values())
    line = (f"{'total':<9}{t['import_kwh']:>14.1f}{t['export_kwh']:>14.1f}{'':>14}"
            f"{t['market_sold_kwh']:>12.1f}{bought:>13.1f}{t['market_gain']:>13.2f}{t['cost']:>10.2f}"
            f"{str(t['visits_on_target']) + '/' + str(t['visits']):>15}")
    if co2_factor is not None:
        line += f"{t['import_kwh'] * co2_factor:>9.2f}"
    print(line)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dias", type=int, default=7)
    parser.add_argument("--inicio", default="2026-01-05", help="AAAA-MM-DD")
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--clima", default=DEFAULT_WEATHER,
                        help="clima de cada dia, separado por vírgula (repete se faltar): ensolarado, "
                             "parcialmente nublado, chuvoso (curva sintética) ou uma data AAAA-MM-DD "
                             "(radiação real do INMET, exige dados/processados/perfil_solar_sp.csv)")
    parser.add_argument("--valor-exportacao", type=float, default=0.0,
                        help="R$ por kWh exportado; premissa, ponto 17 do CONTEXT.md em aberto")
    parser.add_argument("--fator-co2", type=float, default=None,
                        help="kg CO2 por kWh da rede; sem fonte oficial o CO2 não é calculado")
    parser.add_argument("--sem-marketplace", action="store_true",
                        help="desliga o marketplace no cenário com otimização")
    parser.add_argument("--json", metavar="CAMINHO",
                        help="grava o comparativo no formato lido pelo GET /comparison do backend")
    parser.add_argument("--simulacao", default="demo",
                        help="simulation_id gravado no JSON; deve ser o X-Simulation-Id usado nas consultas")
    args = parser.parse_args()

    start = datetime.strptime(args.inicio, "%Y-%m-%d").replace(hour=7)
    weather = [item.strip() for item in args.clima.split(",")]
    common = dict(days=args.dias, start=start, seed=args.semente, weather=weather,
                  export_value=args.valor_exportacao)
    baseline = run(optimized=False, **common)
    optimized = run(optimized=True, market=not args.sem_marketplace, **common)

    print(f"{args.dias} dias a partir de {args.inicio} 07:00; semente {args.semente}; "
          f"exportação a R$ {args.valor_exportacao:.2f}/kWh (premissa); clima: {', '.join(weather)}")
    print_scenario("Sem otimização", baseline, args.fator_co2)
    print_scenario("Com otimização", optimized, args.fator_co2)

    a, b = totals(baseline), totals(optimized)
    print("\nComparativo (com otimização em relação ao cenário sem)")
    print(f"  custo: R$ {a['cost']:.2f} -> R$ {b['cost']:.2f} "
          f"({(b['cost'] - a['cost']) / a['cost'] * 100:+.1f}%)")
    print(f"  energia importada: {a['import_kwh']:.1f} -> {b['import_kwh']:.1f} kWh "
          f"({(b['import_kwh'] - a['import_kwh']) / a['import_kwh'] * 100:+.1f}%)")

    if args.json:
        stamp = "%Y-%m-%dT%H:%M:%S-03:00"
        comparison = {
            "simulation_id": args.simulacao,
            "period": {"from": f"{start:{stamp}}", "to": f"{start + timedelta(days=args.dias):{stamp}}"},
            "baseline": {"cost": a["cost"], "import_kwh": a["import_kwh"]},
            "optimized": {"cost": b["cost"], "import_kwh": b["import_kwh"]},
        }
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(comparison, indent=2), encoding="utf-8")
        print(f"\nComparativo gravado em {args.json}")


if __name__ == "__main__":
    main()
