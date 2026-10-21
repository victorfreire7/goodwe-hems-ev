"""Serviço HTTP do motor de decisão, chamado pelo backend a cada passo (README, seção 3.6).

POST /decide  recebe {readings, ev_targets, export_value_per_kwh, optimized} e devolve
              {commands, trades, offers, orders}.
GET /health   responde {"status": "ok"}.

Usa só a biblioteca padrão. Uso: python -m engine.service (variáveis ENGINE_HOST e ENGINE_PORT)."""
import json
import os
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from engine.dispatch import decide
from engine.tariff import load_tariff, price
from engine.validation import validate_reading
from marketplace.matching import match
from marketplace.settlement import build_book
from simulator.config import ALL_HOUSES, CHARGER_KW
from simulator.house import parse_timestamp

HOUSES = {config.house_id: config for config in ALL_HOUSES}


class RequestError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def decide_step(body, prices):
    """Decide um passo de todas as casas. Levanta RequestError para entrada inválida."""
    try:
        readings = {reading["house_id"]: reading for reading in body["readings"]}
        export_value = float(body["export_value_per_kwh"])
        optimized = bool(body["optimized"])
    except (KeyError, TypeError, ValueError) as error:
        raise RequestError(400, f"Corpo inválido: {error!r}") from error
    if not readings or len(readings) != len(body["readings"]):
        raise RequestError(400, "Lista de leituras vazia ou com casa repetida.")
    commands = {}
    for house_id, reading in readings.items():
        config = HOUSES.get(house_id)
        if config is None:
            raise RequestError(422, f"Casa sem configuração no motor: {house_id}")
        try:
            check = validate_reading(reading, battery_max_power_kw=config.battery_power_kw,
                                     market_model="financial_only", ev_max_power_kw=CHARGER_KW)
            if not check["valid"]:
                raise RequestError(422, f"{house_id}: {check['errors']}")
            commands[house_id] = decide(reading, config.battery_power_kw, prices, optimized)
        except (KeyError, TypeError, ValueError) as error:
            raise RequestError(400, f"{house_id}: leitura malformada ({error!r})") from error
    moment = parse_timestamp(next(iter(readings.values()))["timestamp"])
    offers, orders = build_book(readings, price(moment, prices), export_value) if optimized else ([], [])
    trades = match(offers, orders)
    for trade in trades:
        commands[trade.seller_id]["market"]["sold_kwh"] += trade.quantity_kwh
        commands[trade.buyer_id]["market"]["bought_kwh"] += trade.quantity_kwh
    return {"commands": list(commands.values()), "trades": [asdict(trade) for trade in trades],
            "offers": [asdict(offer) for offer in offers], "orders": [asdict(order) for order in orders]}


def make_handler(prices):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status, payload):
            data = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                self._send(200, {"status": "ok"})
            else:
                self._send(404, {"error": "Rota não encontrada."})

        def do_POST(self):
            if self.path != "/decide":
                return self._send(404, {"error": "Rota não encontrada."})
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                self._send(200, decide_step(body, prices))
            except json.JSONDecodeError:
                self._send(400, {"error": "JSON inválido."})
            except RequestError as error:
                self._send(error.status, {"error": str(error)})

        def log_message(self, format, *args):  # um log por passo (a cada 15 min simulados) é ruído
            pass

    return Handler


def main():
    host, port = os.environ.get("ENGINE_HOST", "127.0.0.1"), int(os.environ.get("ENGINE_PORT", 8000))
    server = ThreadingHTTPServer((host, port), make_handler(load_tariff()))
    print(f"Motor em http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
