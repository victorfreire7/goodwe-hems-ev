"""Casa simulada: geração solar, carga, bateria, carro e rede (README, seção 4)."""
import math
import random
from datetime import datetime, timedelta

from simulator.config import (
    BATTERY_EFFICIENCY, BATTERY_INITIAL_SOC, BATTERY_SOC_MAX, BATTERY_SOC_MIN,
    CHARGER_KW, CLOUD_VARIATION, EV_CAPACITY_KWH, LOAD_PROFILE_KW, LOAD_VARIATION,
    PV_PERFORMANCE, STEP_HOURS, STEP_MINUTES, STEPS_PER_DAY, WEATHER_FACTOR,
)


def parse_timestamp(text):
    """Lê o timestamp da leitura como horário local, sem fuso."""
    return datetime.fromisoformat(text).replace(tzinfo=None)


class House:
    """Uma casa. O ruído de nuvem e de carga é sorteado na criação, então
    não depende dos comandos e os cenários sem e com otimização veem o mesmo dia."""

    def __init__(self, config, start, days, weather, seed):
        self.config = config
        self.start = start
        self.weather = weather
        rng = random.Random(f"{seed}-{config.house_id}")
        steps = days * STEPS_PER_DAY
        self._cloud = [1 + rng.uniform(-CLOUD_VARIATION, CLOUD_VARIATION) for _ in range(steps)]
        self._load = [1 + rng.uniform(-LOAD_VARIATION, LOAD_VARIATION) for _ in range(steps)]
        self.battery_soc = BATTERY_INITIAL_SOC
        self.ev_soc = 0.0
        self._was_connected = False

    def step(self, index, command):
        """Aplica o comando recebido e devolve a leitura do passo (README, seção 4.1).

        Os SOC da leitura são os do fim do passo. Os comandos são limitados
        pela física (potência, SOC, carro conectado); a rede absorve o resto."""
        moment = self.start + timedelta(minutes=STEP_MINUTES * index)
        pv = self._pv_kw(index, moment)
        load = self._load_kw(index, moment)
        car = self.config.car
        connected = car is not None and car.connected_at(moment.hour)
        if connected and not self._was_connected:
            self.ev_soc = car.arrival_soc
        self._was_connected = connected
        ev_kw = self._apply_ev(command["ev_charge_power_kw"], connected)
        battery_kw = self._apply_battery(command["battery_power_kw"])
        return {
            "house_id": self.config.house_id,
            "timestamp": f"{moment:%Y-%m-%dT%H:%M:%S}-03:00",
            "pv_power_kw": pv,
            "load_power_kw": load,
            "battery": {"soc_percent": self.battery_soc, "power_kw": battery_kw},
            "ev": {
                "connected": connected,
                # sem carro conectado, o SOC não é medido
                "soc_percent": self.ev_soc if connected else 0.0,
                "capacity_kwh": EV_CAPACITY_KWH if car else 0.0,
                "target_soc_percent": car.target_soc if car else 0.0,
                "departure_time": car.departure_time if car else None,
                "charge_power_kw": ev_kw,
            },
            "grid_power_kw": load + ev_kw - pv - battery_kw,
        }

    def _pv_kw(self, index, moment):
        hour = moment.hour + (moment.minute + STEP_MINUTES / 2) / 60
        if not 6 < hour < 18:
            return 0.0
        day = (moment.date() - self.start.date()).days
        weather = self.weather[day % len(self.weather)]
        factor = WEATHER_FACTOR[weather]
        if weather == "parcialmente nublado":
            factor *= self._cloud[index]
        power = self.config.kwp * PV_PERFORMANCE * math.sin(math.pi * (hour - 6) / 12) * factor
        return min(power, self.config.inverter_kw)

    def _load_kw(self, index, moment):
        base = next(kw for start, end, kw in LOAD_PROFILE_KW if start <= moment.hour < end)
        return base * self._load[index]

    def _apply_ev(self, requested_kw, connected):
        if not connected:
            return 0.0
        room_kwh = (100 - self.ev_soc) / 100 * EV_CAPACITY_KWH
        kw = min(max(requested_kw, 0.0), CHARGER_KW, room_kwh / STEP_HOURS)
        self.ev_soc = min(100.0, self.ev_soc + kw * STEP_HOURS / EV_CAPACITY_KWH * 100)
        return kw

    def _apply_battery(self, requested_kw):
        capacity = self.config.battery_kwh
        limit = self.config.battery_power_kw
        if requested_kw >= 0:  # descarga
            available_kwh = (self.battery_soc - BATTERY_SOC_MIN) / 100 * capacity
            kw = min(requested_kw, limit, available_kwh * BATTERY_EFFICIENCY / STEP_HOURS)
            self.battery_soc -= kw * STEP_HOURS / BATTERY_EFFICIENCY / capacity * 100
        else:  # carga
            room_kwh = (BATTERY_SOC_MAX - self.battery_soc) / 100 * capacity
            kw = min(-requested_kw, limit, room_kwh / (STEP_HOURS * BATTERY_EFFICIENCY))
            self.battery_soc += kw * STEP_HOURS * BATTERY_EFFICIENCY / capacity * 100
            kw = -kw
        self.battery_soc = min(BATTERY_SOC_MAX, max(BATTERY_SOC_MIN, self.battery_soc))
        return kw
