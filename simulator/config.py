"""Parâmetros da simulação (README, seção 4.3)."""
from dataclasses import dataclass

STEP_MINUTES = 15
STEP_HOURS = STEP_MINUTES / 60
STEPS_PER_DAY = 96

PV_PERFORMANCE = 0.80
BATTERY_EFFICIENCY = 0.95  # na carga e na descarga
BATTERY_SOC_MIN = 10.0
BATTERY_SOC_MAX = 100.0
BATTERY_INITIAL_SOC = 50.0
MODULE_KWH = 3.2  # Lynx F G2, módulo LX F3.2-20
MODULE_POWER_KW = 2.24  # potência nominal por módulo (ficha técnica)
CHARGER_KW = 7.0  # GW7K-HCA-20
EV_CAPACITY_KWH = 60.0

WEATHER_FACTOR = {"ensolarado": 1.0, "parcialmente nublado": 0.6, "chuvoso": 0.25}
CLOUD_VARIATION = 0.20  # variação por passo no dia parcialmente nublado
LOAD_VARIATION = 0.10  # variação por passo na carga da casa

# (hora inicial, hora final, kW); soma 15,0 kWh por dia
LOAD_PROFILE_KW = ((0, 6, 0.3), (6, 9, 0.8), (9, 17, 0.5), (17, 22, 1.2), (22, 24, 0.4))


@dataclass(frozen=True)
class CarConfig:
    arrival_hour: int
    departure_hour: int
    arrival_soc: float
    target_soc: float

    @property
    def departure_time(self):
        return f"{self.departure_hour:02d}:00"

    def connected_at(self, hour):
        if self.arrival_hour < self.departure_hour:
            return self.arrival_hour <= hour < self.departure_hour
        return hour >= self.arrival_hour or hour < self.departure_hour


@dataclass(frozen=True)
class HouseConfig:
    house_id: str
    kwp: float
    inverter_kw: float
    battery_modules: int
    car: CarConfig = None

    @property
    def battery_kwh(self):
        return self.battery_modules * MODULE_KWH

    @property
    def battery_power_kw(self):
        return min(self.battery_modules * MODULE_POWER_KW, self.inverter_kw)


DEFAULT_HOUSES = (
    HouseConfig("casa-01", 6.0, 6.0, 4, CarConfig(18, 7, 30.0, 80.0)),
    HouseConfig("casa-02", 4.0, 6.0, 2, CarConfig(9, 17, 40.0, 80.0)),
    HouseConfig("casa-03", 8.0, 8.0, 4, None),
)
