"""Testes do serviço HTTP do motor: contrato com o backend e laço fechado com o simulador."""
import json
import threading
import unittest
import urllib.error
import urllib.request
from datetime import datetime
from http.server import ThreadingHTTPServer

from engine.metrics import HouseMetrics
from engine.service import decide_step, make_handler, RequestError
from engine.tariff import load_tariff, price
from simulator.client import simulate
from simulator.config import DEFAULT_HOUSES, STEPS_PER_DAY
from simulator.house import House, parse_timestamp
from simulator.scenario import run

WEATHER = ["ensolarado", "parcialmente nublado", "chuvoso"]
START = datetime(2026, 1, 5, 7)
IDLE = {"ev_charge_power_kw": 0.0, "battery_power_kw": 0.0}
PRICES = load_tariff()


def body(readings, optimized=True, export_value=0.0):
    return {"readings": readings, "ev_targets": {}, "export_value_per_kwh": export_value, "optimized": optimized}


def first_readings():
    return [House(config, START, 1, WEATHER, 42).step(0, IDLE) for config in DEFAULT_HOUSES]


class DecideStepTests(unittest.TestCase):
    def test_response_has_the_backend_contract(self):
        result = decide_step(body(first_readings()), PRICES)
        self.assertEqual(set(result), {"commands", "trades", "offers", "orders"})
        self.assertEqual([c["house_id"] for c in result["commands"]], [h.house_id for h in DEFAULT_HOUSES])
        for command in result["commands"]:
            self.assertEqual(set(command), {"house_id", "timestamp", "ev_charge_power_kw",
                                            "battery_power_kw", "market", "reason"})
            self.assertTrue(command["reason"])

    def test_market_in_commands_matches_trades(self):
        houses = [House(config, START, 1, WEATHER, 42) for config in DEFAULT_HOUSES]
        commands = {h.config.house_id: IDLE for h in houses}
        trades = 0
        for index in range(STEPS_PER_DAY):
            readings = [h.step(index, commands[h.config.house_id]) for h in houses]
            result = decide_step(body(readings), PRICES)
            sold = {c["house_id"]: c["market"]["sold_kwh"] for c in result["commands"]}
            bought = {c["house_id"]: c["market"]["bought_kwh"] for c in result["commands"]}
            for trade in result["trades"]:
                self.assertGreater(trade["quantity_kwh"], 0)
                sold[trade["seller_id"]] -= trade["quantity_kwh"]
                bought[trade["buyer_id"]] -= trade["quantity_kwh"]
                trades += 1
            self.assertTrue(all(abs(value) < 1e-9 for value in [*sold.values(), *bought.values()]))
            commands = {c["house_id"]: c for c in result["commands"]}
        self.assertGreater(trades, 0)

    def test_baseline_has_no_market(self):
        result = decide_step(body(first_readings(), optimized=False), PRICES)
        self.assertEqual((result["trades"], result["offers"], result["orders"]), ([], [], []))

    def test_invalid_input(self):
        readings = first_readings()
        for broken, status in [({"readings": readings}, 400), (body([]), 400), (body(readings + readings), 400)]:
            with self.assertRaises(RequestError) as caught:
                decide_step(broken, PRICES)
            self.assertEqual(caught.exception.status, status)
        unknown = first_readings()
        unknown[0]["house_id"] = "casa-99"
        with self.assertRaises(RequestError) as caught:
            decide_step(body(unknown), PRICES)
        self.assertEqual(caught.exception.status, 422)
        unbalanced = first_readings()
        unbalanced[0]["grid_power_kw"] += 1.0
        with self.assertRaises(RequestError) as caught:
            decide_step(body(unbalanced), PRICES)
        self.assertEqual(caught.exception.status, 422)

    def test_closed_loop_through_the_service_matches_the_scenario(self):
        houses = [House(config, START, 1, WEATHER, 42) for config in DEFAULT_HOUSES]
        commands = {h.config.house_id: IDLE for h in houses}
        metrics = {h.config.house_id: HouseMetrics() for h in houses}
        for index in range(STEPS_PER_DAY):
            readings = [h.step(index, commands[h.config.house_id]) for h in houses]
            for reading in readings:
                moment = parse_timestamp(reading["timestamp"])
                metrics[reading["house_id"]].record(reading, price(moment, PRICES), 0.0)
            result = decide_step(body(readings), PRICES)
            commands = {c["house_id"]: c for c in result["commands"]}
        expected = run(days=1, start=START, seed=42, weather=WEATHER, optimized=True)
        for house_id, reference in expected.items():
            self.assertAlmostEqual(metrics[house_id].import_kwh, reference.import_kwh)
            self.assertAlmostEqual(metrics[house_id].pv_kwh, reference.pv_kwh)


class SimulatorClientTests(unittest.TestCase):
    def test_simulate_applies_engine_commands(self):
        steps = []

        def send(readings):
            return decide_step(body(readings), PRICES)["commands"]

        simulate(send, days=1, start=START, seed=42, weather=WEATHER,
                 on_step=lambda index, readings, commands: steps.append((readings, commands)))
        self.assertEqual(len(steps), STEPS_PER_DAY)
        # com o comando do motor, o carro da casa-01 chega ao SOC alvo antes da saída das 07:00 do dia seguinte
        last = steps[-1][0][0]["ev"]
        self.assertGreaterEqual(last["soc_percent"], 79.99)


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(PRICES))
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def post(self, path, data):
        request = urllib.request.Request(self.url + path, data=data, method="POST",
                                         headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def test_health(self):
        with urllib.request.urlopen(self.url + "/health") as response:
            self.assertEqual(json.loads(response.read()), {"status": "ok"})

    def test_decide_over_http(self):
        status, result = self.post("/decide", json.dumps(body(first_readings())).encode())
        self.assertEqual(status, 200)
        self.assertEqual(len(result["commands"]), 3)

    def test_errors_over_http(self):
        self.assertEqual(self.post("/decide", b"{")[0], 400)
        self.assertEqual(self.post("/decide", b"{}")[0], 400)
        self.assertEqual(self.post("/outra", b"{}")[0], 404)


if __name__ == "__main__":
    unittest.main()
