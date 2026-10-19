"""Negocia excedentes de um passo. O motor limita as quantidades disponíveis."""
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Offer:
    house_id: str
    quantity_kwh: float
    export_value_per_kwh: float


@dataclass(frozen=True)
class Order:
    house_id: str
    quantity_kwh: float
    grid_price_per_kwh: float


@dataclass(frozen=True)
class Trade:
    seller_id: str
    buyer_id: str
    quantity_kwh: float
    price_per_kwh: float

    @property
    def total(self):
        return self.quantity_kwh * self.price_per_kwh


def _nonnegative(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Valor deve ser numérico.")
    if not isfinite(value) or value < 0:
        raise ValueError("Valor deve ser finito e não negativo.")


def _validate(items, price_field):
    seen = set()
    for item in items:
        if not isinstance(item.house_id, str) or not item.house_id.strip():
            raise ValueError("house_id obrigatório.")
        if item.house_id in seen:
            raise ValueError("Uma entrada por casa e lado em cada passo.")
        seen.add(item.house_id)
        _nonnegative(item.quantity_kwh)
        _nonnegative(getattr(item, price_field))


def match(offers, orders):
    """Usa preço médio entre piso e teto; só negocia quando piso < teto.

    Desempates usam house_id. As entradas não são alteradas e as sobras
    expiram ao fim da chamada. Persistência por passo cabe ao backend.
    """
    offers, orders = list(offers), list(orders)
    _validate(offers, "export_value_per_kwh")
    _validate(orders, "grid_price_per_kwh")
    sellers = {offer.house_id for offer in offers if offer.quantity_kwh > 0}
    buyers = {order.house_id for order in orders if order.quantity_kwh > 0}
    if sellers & buyers:
        raise ValueError("Uma casa não pode comprar e vender no mesmo passo.")
    offers.sort(key=lambda x: (x.export_value_per_kwh, x.house_id))
    orders.sort(key=lambda x: (-x.grid_price_per_kwh, x.house_id))
    remaining = {offer.house_id: offer.quantity_kwh for offer in offers}
    trades = []
    for order in orders:
        needed = order.quantity_kwh
        for offer in offers:
            if needed <= 0:
                break
            if offer.export_value_per_kwh >= order.grid_price_per_kwh:
                break
            quantity = min(remaining[offer.house_id], needed)
            if quantity <= 0:
                continue
            price = (offer.export_value_per_kwh + order.grid_price_per_kwh) / 2
            trades.append(Trade(offer.house_id, order.house_id, quantity, price))
            remaining[offer.house_id] -= quantity
            needed -= quantity
    return trades
