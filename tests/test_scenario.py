"""Testes da tarifa, da casa simulada e do comparativo sem e com otimização."""
import unittest
from datetime import datetime

from engine.tariff import INTERMEDIATE, OFF_PEAK, PEAK, load_tariff, period
from simulator.config import ALL_HOUSES, BATTERY_SOC_MAX, BATTERY_SOC_MIN, DEFAULT_HOUSES, STEPS_PER_DAY, houses_for
from simulator.house import House
from simulator.scenario import run
from simulator.solar import PROFILE, irradiance_at

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


class SolarTests(unittest.TestCase):
    def test_interpolation_between_hours(self):
        profile = {datetime(2026, 1, 5, 7): 0.4, datetime(2026, 1, 5, 8): 0.8}
        # o passo das 06:30 tem ponto médio 06:37:30, a 7/8 do caminho entre os pontos das horas 6 e 7
        self.assertAlmostEqual(irradiance_at(profile, datetime(2026, 1, 5, 6, 30), 15), 0.45)
        self.assertEqual(irradiance_at(profile, datetime(2026, 1, 5, 3, 0), 15), 0.0)

    @unittest.skipUnless(PROFILE.exists(), "perfil_solar_sp.csv não gerado")
    def test_real_day_generates_within_inverter_limit(self):
        house = House(DEFAULT_HOUSES[0], datetime(2026, 9, 27, 7), 1, ["2026-09-27"], 42)
        idle = {"ev_charge_power_kw": 0.0, "battery_power_kw": 0.0}
        readings = [house.step(index, idle) for index in range(STEPS_PER_DAY)]
        self.assertGreater(max(r["pv_power_kw"] for r in readings), 0)
        self.assertLessEqual(max(r["pv_power_kw"] for r in readings), DEFAULT_HOUSES[0].inverter_kw)
        self.assertEqual(readings[80]["pv_power_kw"], 0.0)  # 03:00

    @unittest.skipUnless(PROFILE.exists(), "perfil_solar_sp.csv não gerado")
    def test_scenario_runs_with_real_days(self):
        metrics = run(days=2, start=datetime(2026, 9, 27, 7), seed=42,
                      weather=["2026-09-27", "2026-09-23"], optimized=True)
        self.assertGreater(sum(m.pv_kwh for m in metrics.values()), 0)


class TenHousesTests(unittest.TestCase):
    def test_ten_houses_run_validate_and_reach_the_car_target(self):
        metrics = run(days=3, start=START, seed=42, weather=WEATHER, optimized=True, houses=houses_for(10))
        self.assertEqual(len(metrics), 10)
        for house in ALL_HOUSES:
            if house.car is not None:
                self.assertEqual(metrics[house.house_id].visits_on_target, metrics[house.house_id].visits, house.house_id)
        self.assertAlmostEqual(sum(m.market_sold_kwh for m in metrics.values()),
                               sum(m.market_bought_kwh for m in metrics.values()))

    def test_house_count_limits(self):
        for count in (2, 11):
            with self.assertRaises(ValueError):
                houses_for(count)


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
