"""Métricas por casa: energia, custo, autoconsumo e carro no SOC alvo (README, seção 10)."""
from datetime import timedelta

from simulator.config import STEP_HOURS, STEP_MINUTES
from simulator.house import parse_timestamp

TARGET_TOLERANCE = 0.01  # pontos percentuais de SOC


class HouseMetrics:
    def __init__(self):
        self.import_kwh = 0.0
        self.export_kwh = 0.0
        self.pv_kwh = 0.0
        self.cost = 0.0
        self.market_sold_kwh = 0.0
        self.market_bought_kwh = 0.0
        self.market_gain = 0.0  # R$ que o marketplace tirou do custo da casa
        self.visits = 0  # idas e vindas do carro concluídas (do plug-in até a saída)
        self.visits_on_target = 0
        self._last_ev = None

    def record(self, reading, price_kwh, export_value):
        grid = reading["grid_power_kw"]
        imported = max(grid, 0.0) * STEP_HOURS
        exported = max(-grid, 0.0) * STEP_HOURS
        self.import_kwh += imported
        self.export_kwh += exported
        self.pv_kwh += reading["pv_power_kw"] * STEP_HOURS
        self.cost += imported * price_kwh - exported * export_value
        ev = reading["ev"]
        if ev["connected"]:
            self._last_ev = ev
        elif self._last_ev is not None:
            self._close_visit()

    def record_trade(self, role, quantity_kwh, trade_price, reference_price):
        """Acerta uma negociação do marketplace.

        Vendedor ganha (preço - valor da exportação); comprador economiza (tarifa - preço)."""
        if role == "seller":
            self.market_sold_kwh += quantity_kwh
            gain = quantity_kwh * (trade_price - reference_price)
        else:
            self.market_bought_kwh += quantity_kwh
            gain = quantity_kwh * (reference_price - trade_price)
        self.market_gain += gain
        self.cost -= gain

    def finish(self, last_reading):
        """Fecha a visita em andamento se o carro sai logo após o último passo."""
        if self._last_ev is None:
            return
        next_moment = parse_timestamp(last_reading["timestamp"]) + timedelta(minutes=STEP_MINUTES)
        if f"{next_moment:%H:%M}" == self._last_ev["departure_time"]:
            self._close_visit()

    def _close_visit(self):
        ev = self._last_ev
        self.visits += 1
        if ev["soc_percent"] >= ev["target_soc_percent"] - TARGET_TOLERANCE:
            self.visits_on_target += 1
        self._last_ev = None

    @property
    def self_consumption_percent(self):
        return (self.pv_kwh - self.export_kwh) / self.pv_kwh * 100 if self.pv_kwh else 0.0
