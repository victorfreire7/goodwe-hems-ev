"""Radiação solar real do INMET, gerada por scripts/preparar_geracao_inmet.py (README, seção 4.4)."""
import csv
from datetime import datetime, timedelta
from functools import cache
from pathlib import Path

PROFILE = Path(__file__).resolve().parent.parent / "dados" / "processados" / "perfil_solar_sp.csv"
HOUR = timedelta(hours=1)


@cache
def load_irradiance(path=PROFILE):
    """Devolve {hora cheia local: kW/m2}. A hora H é a média de (H-1, H], como no INMET."""
    with open(path, encoding="utf-8", newline="") as file:
        return {datetime.fromisoformat(row["timestamp_local"]).replace(tzinfo=None): float(row["irradiancia_kw_m2"])
                for row in csv.DictReader(file, delimiter=";")}


def irradiance_at(profile, moment, step_minutes):
    """Irradiância (kW/m2) no meio do passo que começa em `moment`, por interpolação linear.

    Cada valor horário vale para o meio da hora anterior ao seu rótulo; hora sem medição vale zero."""
    label = moment + timedelta(minutes=step_minutes / 2) + HOUR / 2
    base = label.replace(minute=0, second=0, microsecond=0)
    fraction = (label - base) / HOUR
    return profile.get(base, 0.0) * (1 - fraction) + profile.get(base + HOUR, 0.0) * fraction
