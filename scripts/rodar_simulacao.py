"""Roda o simulador contra a API do backend, passo a passo (README, seções 3.4 e 3.5).

O backend precisa estar no ar (docker compose up) com ENGINE_MODE=http para as decisões do motor;
em ENGINE_MODE=neutral os comandos são zerados. Cada execução usa um --simulacao diferente, porque
o backend recusa passos que já recebeu com leituras diferentes (409).

Uso: python scripts/rodar_simulacao.py [--url http://127.0.0.1:3000] [--simulacao demo] [--dias 1]
         [--inicio 2026-01-05] [--semente 42] [--clima "ensolarado,chuvoso"] [--segundos-por-passo 0]
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simulator.client import http_sender, simulate  # noqa: E402
from simulator.config import STEPS_PER_DAY  # noqa: E402

DEFAULT_WEATHER = "ensolarado,ensolarado,parcialmente nublado,chuvoso,ensolarado,parcialmente nublado,ensolarado"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default="http://127.0.0.1:3000")
    parser.add_argument("--simulacao", default="demo", help="valor do cabeçalho X-Simulation-Id")
    parser.add_argument("--dias", type=int, default=1)
    parser.add_argument("--inicio", default="2026-01-05", help="AAAA-MM-DD; a simulação começa às 07:00")
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--clima", default=DEFAULT_WEATHER,
                        help="clima de cada dia: ensolarado, parcialmente nublado, chuvoso ou uma data AAAA-MM-DD")
    parser.add_argument("--segundos-por-passo", type=float, default=0.0,
                        help="0 = modo lote; 1 = modo acelerado (96 s por dia simulado)")
    args = parser.parse_args()

    start = datetime.strptime(args.inicio, "%Y-%m-%d").replace(hour=7)
    weather = [item.strip() for item in args.clima.split(",")]

    def progress(index, readings, commands):
        if (index + 1) % STEPS_PER_DAY == 0:
            print(f"dia {(index + 1) // STEPS_PER_DAY} concluído ({readings[0]['timestamp']})")

    print(f"Simulação '{args.simulacao}' em {args.url}: {args.dias} dia(s) a partir de {args.inicio} 07:00")
    simulate(http_sender(args.url, args.simulacao), days=args.dias, start=start, seed=args.semente,
             weather=weather, seconds_per_step=args.segundos_por_passo, on_step=progress)


if __name__ == "__main__":
    main()
