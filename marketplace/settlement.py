"""Monta ofertas e ordens de um passo a partir das leituras das casas e negocia (README, seção 6).

Vendedor: casa que exportou no passo; piso = valor da exportação.
Comprador: casa que importou da rede enquanto carregava o carro; quantidade =
min(importação, energia do carro); teto = tarifa da rede no passo."""
from marketplace.matching import Offer, Order, match
from simulator.config import STEP_HOURS


def build_book(readings, grid_price, export_value):
    """Devolve (ofertas, ordens) do passo. `readings` é {house_id: leitura}."""
    offers, orders = [], []
    for house_id, reading in readings.items():
        grid_kwh = reading["grid_power_kw"] * STEP_HOURS
        if grid_kwh < 0:
            offers.append(Offer(house_id, -grid_kwh, export_value))
            continue
        quantity = min(grid_kwh, reading["ev"]["charge_power_kw"] * STEP_HOURS)
        if quantity > 0:
            orders.append(Order(house_id, quantity, grid_price))
    return offers, orders


def trade_step(readings, grid_price, export_value):
    return match(*build_book(readings, grid_price, export_value))
