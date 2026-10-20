"""Roda um cenário completo (sem ou com otimização) em memória, sem backend."""
from engine.dispatch import decide
from engine.metrics import HouseMetrics
from engine.tariff import load_tariff, price
from engine.validation import validate_reading
from simulator.config import CHARGER_KW, DEFAULT_HOUSES, STEPS_PER_DAY
from simulator.house import House, parse_timestamp

IDLE_COMMAND = {"ev_charge_power_kw": 0.0, "battery_power_kw": 0.0}


def run(*, days, start, seed, weather, optimized, export_value=0.0, houses=DEFAULT_HOUSES, prices=None):
    """Simula `days` dias a partir de `start` e devolve {house_id: HouseMetrics}.

    Cada leitura passa por `validate_reading`; leitura inválida interrompe a execução."""
    prices = prices or load_tariff()
    simulated = [House(config, start, days, weather, seed) for config in houses]
    commands = {house.config.house_id: IDLE_COMMAND for house in simulated}
    metrics = {house.config.house_id: HouseMetrics() for house in simulated}
    last = {}
    for index in range(days * STEPS_PER_DAY):
        for house in simulated:
            config = house.config
            reading = house.step(index, commands[config.house_id])
            check = validate_reading(
                reading, battery_max_power_kw=config.battery_power_kw,
                market_model="financial_only", ev_max_power_kw=CHARGER_KW)
            if not check["valid"]:
                raise RuntimeError(f"{config.house_id} {reading['timestamp']}: {check['errors']}")
            moment = parse_timestamp(reading["timestamp"])
            metrics[config.house_id].record(reading, price(moment, prices), export_value)
            commands[config.house_id] = decide(reading, config.battery_power_kw, prices, optimized)
            last[config.house_id] = reading
    for house_id, house_metrics in metrics.items():
        house_metrics.finish(last[house_id])
    return metrics
