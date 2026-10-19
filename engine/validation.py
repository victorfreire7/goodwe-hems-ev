"""Verifica SOC, potência e balanço de leituras do mesmo intervalo de 15 min."""
from math import isfinite


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError("Leitura deve conter números finitos.")
    return value


def validate_reading(reading, *, battery_max_power_kw, market_model,
                     ev_max_power_kw=7, tolerance_kw=1e-6):
    """Retorna erros físicos; entrada malformada gera ValueError ou KeyError.

    battery.power_kw positivo descarrega; grid_power_kw positivo importa.
    Limites de SOC seguem o README. Não valida evolução temporal da bateria.
    """
    if market_model not in ("ideal_microgrid", "financial_only"):
        raise ValueError("Modelo do marketplace deve ser explícito.")
    limit = _number(battery_max_power_kw)
    ev_limit = _number(ev_max_power_kw)
    tolerance = _number(tolerance_kw)
    if limit <= 0 or ev_limit <= 0 or tolerance <= 0:
        raise ValueError("Limite e tolerância devem ser positivos.")
    pv = _number(reading["pv_power_kw"])
    load = _number(reading["load_power_kw"])
    grid = _number(reading["grid_power_kw"])
    battery = reading["battery"]
    ev = reading["ev"]
    power = _number(battery["power_kw"])
    charge = _number(ev["charge_power_kw"])
    battery_soc = _number(battery["soc_percent"])
    ev_soc = _number(ev["soc_percent"])
    if not isinstance(ev["connected"], bool):
        raise ValueError("connected deve ser booleano.")
    market = reading.get("market", {})
    sold = _number(market.get("sold_kwh", 0))
    bought = _number(market.get("bought_kwh", 0))
    errors = []
    if min(pv, load, charge, sold, bought) < 0:
        errors.append("negative_energy_or_power")
    if sold > 0 and bought > 0:
        errors.append("simultaneous_market_buy_and_sell")
    if not 10 <= battery_soc <= 100:
        errors.append("battery_soc_out_of_bounds")
    if not 0 <= ev_soc <= 100:
        errors.append("ev_soc_out_of_bounds")
    if abs(power) > limit + tolerance:
        errors.append("battery_power_exceeded")
    if charge > ev_limit + tolerance:
        errors.append("ev_power_exceeded")
    if not ev["connected"] and abs(charge) > tolerance:
        errors.append("disconnected_ev_charging")
    residual = pv + power + grid - load - charge
    if market_model == "ideal_microgrid":
        residual += (bought - sold) / 0.25
    if abs(residual) > tolerance:
        errors.append("energy_balance_mismatch")
    return {"valid": not errors, "errors": errors, "balance_residual_kw": residual}
