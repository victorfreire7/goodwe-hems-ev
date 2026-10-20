"""Testes da tarifa, da casa simulada e do comparativo sem e com otimização."""
import unittest
from datetime import datetime

from engine.tariff import INTERMEDIATE, OFF_PEAK, PEAK, load_tariff, period
from simulator.config import BATTERY_SOC_MAX, BATTERY_SOC_MIN, DEFAULT_HOUSES
from simulator.house import House
from simulator.scenario import run

WEATHER = ["ensolarado", "parcialmente nublado", "chuvoso"]
START = datetime(2026, 1, 5, 7)  # segunda-feira


def execute(optimized, days=3, seed=42):
    return run(days=days, start=START, seed=seed, weather=WEATHER, optimized=optimized)


class TariffTests(unittest.TestCase):
    def test_periods_on_weekday(self):
        cases = [((16, 29), OFF_PEAK), ((16, 30), INTERMEDIATE), ((17, 29), INTERMEDIATE),
                 ((17, 30), PEAK), ((20, 29), PEAK), ((20, 30), INTERMEDIATE),
                 ((21, 29), INTERMEDIATE), ((21, 30), OFF_PEAK), ((3, 0), OFF_PEAK)]
        for (hour, minute), expected in cases:
            with self.subTest(hour=hour, minute=minute):
                self.assertEqual(period(datetime(2026, 1, 5, hour, minute)), expected)

    def test_weekend_and_holiday_are_off_peak(self):
        self.assertEqual(period(datetime(2026, 1, 10, 18, 0)), OFF_PEAK)  # sábado
        self.assertEqual(period(datetime(2026, 9, 7, 18, 0)), OFF_PEAK)  # Independência, segunda

    def test_tariff_file_ignores_scee_rows(self):
        prices = load_tariff()
        self.assertAlmostEqual(prices[OFF_PEAK], 0.6692)
        self.assertAlmostEqual(prices[INTERMEDIATE], 0.9845)
        self.assertAlmostEqual(prices[PEAK], 1.4803)


class HouseTests(unittest.TestCase):
    def house(self, index=0):
        return House(DEFAULT_HOUSES[index], START, 3, WEATHER, 42)

    def test_battery_stays_within_soc_and_power_limits(self):
        house = self.house()
        limit = house.config.battery_power_kw
        for index, requested in enumerate([100.0] * 100 + [-100.0] * 100):
            reading = house.step(index, {"ev_charge_power_kw": 0.0, "battery_power_kw": requested})
            self.assertGreaterEqual(reading["battery"]["soc_percent"], BATTERY_SOC_MIN)
            self.assertLessEqual(reading["battery"]["soc_percent"], BATTERY_SOC_MAX)
            self.assertLessEqual(abs(reading["battery"]["power_kw"]), limit + 1e-9)

    def test_disconnected_car_is_not_charged(self):
        reading = self.house().step(0, {"ev_charge_power_kw": 7.0, "battery_power_kw": 0.0})
        self.assertFalse(reading["ev"]["connected"])  # 07:00: o carro da casa-01 já saiu
        self.assertEqual(reading["ev"]["charge_power_kw"], 0.0)

    def test_house_without_car(self):
        reading = self.house(2).step(0, {"ev_charge_power_kw": 7.0, "battery_power_kw": 0.0})
        self.assertFalse(reading["ev"]["connected"])
        self.assertEqual(reading["ev"]["charge_power_kw"], 0.0)


class ScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # run() valida cada leitura (balanço, SOC, limites de potência) e falha se alguma for inválida
        cls.baseline = execute(optimized=False)
        cls.optimized = execute(optimized=True)

    def test_same_seed_is_reproducible(self):
        again = execute(optimized=True)
        for house_id, metrics in self.optimized.items():
            self.assertEqual(metrics.cost, again[house_id].cost)
            self.assertEqual(metrics.import_kwh, again[house_id].import_kwh)

    def test_scenarios_see_the_same_weather(self):
        for house_id, metrics in self.baseline.items():
            self.assertAlmostEqual(metrics.pv_kwh, self.optimized[house_id].pv_kwh)

    def test_car_reaches_target_in_every_visit(self):
        for scenario in (self.baseline, self.optimized):
            for house_id in ("casa-01", "casa-02"):
                self.assertEqual(scenario[house_id].visits, 3)
                self.assertEqual(scenario[house_id].visits_on_target, 3)
            self.assertEqual(scenario["casa-03"].visits, 0)

    def test_optimization_reduces_total_cost(self):
        self.assertLess(sum(m.cost for m in self.optimized.values()),
                        sum(m.cost for m in self.baseline.values()))

    def test_market_sold_equals_bought(self):
        sold = sum(m.market_sold_kwh for m in self.optimized.values())
        bought = sum(m.market_bought_kwh for m in self.optimized.values())
        self.assertGreater(sold, 0)
        self.assertAlmostEqual(sold, bought)

    def test_baseline_has_no_market(self):
        for metrics in self.baseline.values():
            self.assertEqual(metrics.market_sold_kwh, 0.0)
            self.assertEqual(metrics.market_gain, 0.0)

    def test_market_lowers_cost_without_changing_physics(self):
        without_market = run(days=3, start=START, seed=42, weather=WEATHER, optimized=True, market=False)
        for house_id, metrics in self.optimized.items():
            self.assertAlmostEqual(metrics.import_kwh, without_market[house_id].import_kwh)  # financial_only
            self.assertAlmostEqual(metrics.cost + metrics.market_gain, without_market[house_id].cost)
        self.assertLess(sum(m.cost for m in self.optimized.values()),
                        sum(m.cost for m in without_market.values()))


if __name__ == "__main__":
    unittest.main()
