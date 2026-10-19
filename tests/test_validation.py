import copy
import unittest
from engine.validation import validate_reading
from marketplace.matching import Offer, Order, match


def reading():
    return {"pv_power_kw": 4.2, "load_power_kw": 0.9, "grid_power_kw": 0,
            "battery": {"soc_percent": 62, "power_kw": -1.5},
            "ev": {"connected": True, "soc_percent": 35, "charge_power_kw": 1.8}}


class ValidationTests(unittest.TestCase):
    def check(self, data, model="ideal_microgrid"):
        return validate_reading(data, battery_max_power_kw=6, market_model=model)

    def test_reference_balance(self):
        result = self.check(reading())
        self.assertTrue(result["valid"])
        self.assertAlmostEqual(result["balance_residual_kw"], 0)

    def test_broken_balance(self):
        data = reading()
        data["grid_power_kw"] = 0.1
        self.assertIn("energy_balance_mismatch", self.check(data)["errors"])

    def test_simultaneous_market_flows_are_rejected_even_when_balanced(self):
        for model in ("ideal_microgrid", "financial_only"):
            for quantity in (1, 1e-9):
                with self.subTest(model=model, quantity=quantity):
                    data = reading()
                    data["market"] = {"sold_kwh": quantity, "bought_kwh": quantity}
                    result = self.check(data, model)
                    self.assertAlmostEqual(result["balance_residual_kw"], 0)
                    self.assertFalse(result["valid"])
                    self.assertIn("simultaneous_market_buy_and_sell", result["errors"])

    def test_one_way_market_flow_is_allowed(self):
        for market, grid in [({"sold_kwh": 0.25, "bought_kwh": 0}, 1),
                             ({"sold_kwh": 0, "bought_kwh": 0.25}, -1)]:
            with self.subTest(market=market):
                data = reading()
                data["market"] = market
                data["grid_power_kw"] = grid
                self.assertTrue(self.check(data)["valid"])

    def test_power_signs(self):
        data = reading()
        data.update(pv_power_kw=0, load_power_kw=2, grid_power_kw=1)
        data["battery"]["power_kw"] = 1
        data["ev"]["charge_power_kw"] = 0
        self.assertTrue(self.check(data)["valid"])
        data.update(pv_power_kw=3, grid_power_kw=-2)
        self.assertTrue(self.check(data)["valid"])

    def test_limits(self):
        cases = [("battery", "soc_percent", 9, "battery_soc_out_of_bounds"),
                 ("battery", "soc_percent", 101, "battery_soc_out_of_bounds"),
                 ("battery", "power_kw", -6.1, "battery_power_exceeded"),
                 ("ev", "soc_percent", -1, "ev_soc_out_of_bounds"),
                 ("ev", "soc_percent", 101, "ev_soc_out_of_bounds"),
                 ("ev", "charge_power_kw", 7.1, "ev_power_exceeded"),
                 ("ev", "charge_power_kw", -1, "negative_energy_or_power"),
                 ("ev", "connected", False, "disconnected_ev_charging")]
        for group, field, value, error in cases:
            with self.subTest(field=field, value=value):
                data = reading()
                data[group][field] = value
                self.assertIn(error, self.check(data)["errors"])

    def test_soc_boundaries(self):
        for battery_soc in (10, 100):
            for ev_soc in (0, 100):
                data = reading()
                data["battery"]["soc_percent"] = battery_soc
                data["ev"]["soc_percent"] = ev_soc
                self.assertTrue(self.check(data)["valid"])

    def test_malformed_input(self):
        for value in (float("nan"), float("inf"), True, "4.2"):
            data = reading()
            data["pv_power_kw"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.check(data)
        with self.assertRaises(ValueError):
            self.check(reading(), model="unknown")
        data = reading()
        data["ev"]["connected"] = "false"
        with self.assertRaises(ValueError):
            self.check(data)

    def test_marketplace_to_physical_balance(self):
        trade = match([Offer("seller", 0.5, 0.2)], [Order("buyer", 0.5, 0.8)])[0]
        seller = reading()
        seller.update(pv_power_kw=3, load_power_kw=1)
        seller["battery"]["power_kw"] = 0
        seller["ev"].update(connected=False, charge_power_kw=0)
        seller["market"] = {"sold_kwh": trade.quantity_kwh}
        buyer = copy.deepcopy(seller)
        buyer.update(pv_power_kw=0, load_power_kw=0)
        buyer["ev"].update(connected=True, charge_power_kw=2)
        buyer["market"] = {"bought_kwh": trade.quantity_kwh}
        self.assertTrue(self.check(seller)["valid"])
        self.assertTrue(self.check(buyer)["valid"])
        self.assertFalse(self.check(buyer, "financial_only")["valid"])
        buyer["grid_power_kw"] = 2
        self.assertTrue(self.check(buyer, "financial_only")["valid"])


if __name__ == "__main__":
    unittest.main()
