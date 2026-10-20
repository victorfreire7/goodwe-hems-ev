"""Tarifa branca da Enel SP e postos horários (README, seção 5.3)."""
import csv
from pathlib import Path

DEFAULT_FILE = Path(__file__).resolve().parent.parent / "dados" / "processados" / "tarifa_enel_sp_branca.csv"
OFF_PEAK, INTERMEDIATE, PEAK = "Fora ponta", "Intermediário", "Ponta"
# Feriados nacionais de data fixa; feriados móveis não estão incluídos.
HOLIDAYS = {(1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (11, 20), (12, 25)}


def load_tariff(path=DEFAULT_FILE):
    """Devolve {posto: R$/kWh} (TUSD mais TE, sem tributos), sem as linhas SCEE."""
    prices = {}
    with open(path, encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file, delimiter=";"):
            if row["DscDetalhe"] == "Não se aplica":
                prices[row["NomPostoTarifario"]] = float(row["TUSD_mais_TE_R$_por_kWh"])
    if set(prices) != {OFF_PEAK, INTERMEDIATE, PEAK}:
        raise ValueError(f"Tarifa incompleta em {path}: {sorted(prices)}")
    return prices


def period(moment):
    """Posto horário do passo que começa em `moment` (datetime local)."""
    if moment.weekday() >= 5 or (moment.month, moment.day) in HOLIDAYS:
        return OFF_PEAK
    minutes = moment.hour * 60 + moment.minute
    if 17 * 60 + 30 <= minutes < 20 * 60 + 30:
        return PEAK
    if 16 * 60 + 30 <= minutes < 17 * 60 + 30 or 20 * 60 + 30 <= minutes < 21 * 60 + 30:
        return INTERMEDIATE
    return OFF_PEAK


def price(moment, prices):
    return prices[period(moment)]
