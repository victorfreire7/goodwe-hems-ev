"""Decisão de despacho a cada passo (README, seção 5.1).

A decisão usa a leitura do passo atual como estimativa do próximo (persistência):
o comando vale para o passo seguinte (README, seção 4.2)."""
import math
from datetime import timedelta

from engine.tariff import price
from simulator.config import CHARGER_KW, STEP_HOURS, STEP_MINUTES
from simulator.house import parse_timestamp

STEP = timedelta(minutes=STEP_MINUTES)


def _next_departure(moment, departure_time):
    hour, minute = map(int, departure_time.split(":"))
    departure = moment.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return departure if departure > moment else departure + timedelta(days=1)


def _ev_baseline(reading):
    """Sem otimização: carga máxima assim que conectado, até o SOC alvo."""
    ev = reading["ev"]
    needed_kwh = (ev["target_soc_percent"] - ev["soc_percent"]) / 100 * ev["capacity_kwh"]
    if not ev["connected"] or needed_kwh <= 1e-9:
        return 0.0, "sem carro para carregar"
    return min(CHARGER_KW, needed_kwh / STEP_HOURS), "carga máxima ao conectar"


def _ev_optimized(reading, moment, prices):
    """Com otimização: horários baratos, excedente solar e prazo de saída."""
    ev = reading["ev"]
    if not ev["connected"]:
        return 0.0, "carro desconectado"
    needed_kwh = (ev["target_soc_percent"] - ev["soc_percent"]) / 100 * ev["capacity_kwh"]
    if needed_kwh <= 1e-9:
        return 0.0, "carro no SOC alvo"
    cap_kw = needed_kwh / STEP_HOURS
    steps_left = int((_next_departure(moment, ev["departure_time"]) - moment) / STEP)
    steps_needed = math.ceil(needed_kwh / (CHARGER_KW * STEP_HOURS) - 1e-9)
    if steps_left <= steps_needed:
        return min(CHARGER_KW, cap_kw), "prazo de saída: carga máxima para atingir o SOC alvo"
    moments = [moment + i * STEP for i in range(steps_left)]
    cheapest = sorted(range(steps_left), key=lambda i: (price(moments[i], prices), i))[:steps_needed]
    if 0 in cheapest:
        return min(CHARGER_KW, cap_kw), "carga no horário mais barato antes da saída"
    surplus = reading["pv_power_kw"] - reading["load_power_kw"]
    if surplus > 0:
        return min(CHARGER_KW, surplus, cap_kw), "excedente solar direcionado ao carro"
    return 0.0, "aguardando horário mais barato"


def decide(reading, battery_power_kw, prices, optimized):
    """Devolve o comando da casa (README, seção 4.2) para o passo seguinte."""
    moment = parse_timestamp(reading["timestamp"]) + STEP
    if optimized:
        ev_kw, reason = _ev_optimized(reading, moment, prices)
    else:
        ev_kw, reason = _ev_baseline(reading)
    balance = reading["pv_power_kw"] - reading["load_power_kw"] - ev_kw
    if balance > 0:
        battery_kw = -min(balance, battery_power_kw)
        reason += "; excedente solar para a bateria"
    else:
        battery_kw = min(-balance, battery_power_kw)
        reason += "; bateria cobre o déficit"
    return {
        "house_id": reading["house_id"],
        "timestamp": reading["timestamp"],
        "ev_charge_power_kw": ev_kw,
        "battery_power_kw": battery_kw,
        "market": {"sold_kwh": 0.0, "bought_kwh": 0.0},
        "reason": reason,
    }
