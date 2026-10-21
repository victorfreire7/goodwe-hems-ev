"""Mede o erro médio absoluto (MAE) das previsões de geração solar sobre a radiação real do INMET.

Prevê cada hora de sol (06:00 a 17:00, rótulo da hora) com dados anteriores e compara com a medição. O erro sai em
kW de uma casa de referência (6 kWp, fator de desempenho 0,80, como a casa-01) e em kW/m2. Só entram as horas em que
todas as previsões existem, para a comparação ser justa.

Uso: python scripts/avaliar_previsao.py   (exige dados/processados/perfil_solar_sp.csv)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.forecast import persistence, same_hour_average
from simulator.solar import load_irradiance

KWP, PERFORMANCE = 6.0, 0.80
SUN_HOURS = range(6, 18)
METHODS = {"persistência (hora anterior)": persistence, "média da mesma hora nos 7 dias anteriores": same_hour_average}


def main():
    profile = load_irradiance()
    errors = {name: [] for name in METHODS}
    for hour, real in sorted(profile.items()):
        if hour.hour not in SUN_HOURS:
            continue
        forecasts = {name: method(profile, hour) for name, method in METHODS.items()}
        if None in forecasts.values():
            continue
        for name, forecast in forecasts.items():
            errors[name].append(abs(forecast - real))
    count = len(next(iter(errors.values())))
    if not count:
        raise SystemExit("Nenhuma hora com histórico suficiente.")
    print(f"Horas avaliadas: {count}")
    for name, values in errors.items():
        mae = sum(values) / count
        print(f"  {name}: MAE {mae:.4f} kW/m2 = {mae * KWP * PERFORMANCE:.3f} kW (casa de {KWP:.0f} kWp)")


if __name__ == "__main__":
    main()
