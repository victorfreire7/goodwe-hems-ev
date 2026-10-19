"""Testes das regras de preço e distribuição de energia."""
import unittest
from marketplace.matching import Offer, Order, match


class MarketplaceTests(unittest.TestCase):
    def test_partial_fill_and_price(self):
        trades = match([Offer("seller", 2, 0.4)], [Order("buyer", 3, 1.0)])
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].quantity_kwh, 2)
        self.assertAlmostEqual(trades[0].price_per_kwh, 0.7)
        self.assertAlmostEqual(trades[0].total, 1.4)

    def test_competing_buyers_do_not_spend_same_energy(self):
        trades = match([Offer("s", 2, 0.2)],
                       [Order("b1", 2, 0.8), Order("b2", 1.5, 1.0)])
        self.assertEqual([(t.buyer_id, t.quantity_kwh) for t in trades],
                         [("b2", 1.5), ("b1", 0.5)])

    def test_cheapest_seller_first(self):
        trades = match([Offer("s1", 2, 0.5), Offer("s2", 1, 0.2)],
                       [Order("b", 2, 1)])
        self.assertEqual([(t.seller_id, t.quantity_kwh) for t in trades],
                         [("s2", 1), ("s1", 1)])

    def test_ties_and_input_order(self):
        offers = [Offer("s2", 1, 0.2), Offer("s1", 1, 0.2)]
        orders = [Order("b2", 1, 1), Order("b1", 1, 1)]
        trades = match(offers, orders)
        self.assertEqual(trades, match(reversed(offers), reversed(orders)))
        self.assertEqual(trades[0].seller_id, "s1")
        self.assertEqual(trades[0].buyer_id, "b1")
        self.assertEqual(offers[0].house_id, "s2")

    def test_house_cannot_buy_and_sell(self):
        with self.assertRaises(ValueError):
            match([Offer("a", 1, 0.2)], [Order("a", 1, 1)])

    def test_circular_trade_is_rejected(self):
        with self.assertRaises(ValueError):
            match([Offer("a", 1, 0.2), Offer("b", 1, 0.3)],
                  [Order("a", 1, 0.9), Order("b", 1, 1)])

    def test_zero_offer_does_not_block_buyer(self):
        trades = match([Offer("a", 0, 0.2), Offer("b", 1, 0.3)],
                       [Order("a", 1, 1)])
        self.assertEqual(trades[0].seller_id, "b")

    def test_no_market_or_no_advantage(self):
        for offers, orders in [([], []), ([Offer("s", 1, 0.4)], []),
                               ([], [Order("b", 1, 1)]),
                               ([Offer("s", 1, 1)], [Order("b", 1, 1)]),
                               ([Offer("s", 1, 2)], [Order("b", 1, 1)]),
                               ([Offer("s", 0, 0.2)], [Order("b", 1, 1)])]:
            with self.subTest(offers=offers, orders=orders):
                self.assertEqual(match(offers, orders), [])

    def test_invalid_values_and_duplicate_houses(self):
        for value in [-1, float("nan"), float("inf"), True, "1"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                match([Offer("s", value, 0.2)], [])
            with self.subTest(price=value), self.assertRaises(ValueError):
                match([], [Order("b", 1, value)])
        with self.assertRaises(ValueError):
            match([Offer("s", 1, 0.2), Offer("s", 1, 0.3)], [])
        with self.assertRaises(ValueError):
            match([], [Order("b", 1, 1), Order("b", 1, 1)])
        with self.assertRaises(ValueError):
            match([Offer("", 1, 0.2)], [])

    def test_trade_totals_respect_offer_and_order_limits(self):
        offers = [Offer("s1", 0.75, 0.3), Offer("s2", 0.5, 0.4)]
        orders = [Order("b1", 1, 0.9), Order("b2", 1, 0.8)]
        trades = match(offers, orders)
        for trade in trades:
            self.assertLess(trade.price_per_kwh, next(
                o.grid_price_per_kwh for o in orders if o.house_id == trade.buyer_id))
            self.assertGreater(trade.price_per_kwh, next(
                o.export_value_per_kwh for o in offers if o.house_id == trade.seller_id))
        for offer in offers:
            sold = sum(t.quantity_kwh for t in trades if t.seller_id == offer.house_id)
            self.assertLessEqual(sold, offer.quantity_kwh)
        for order in orders:
            bought = sum(t.quantity_kwh for t in trades if t.buyer_id == order.house_id)
            self.assertLessEqual(bought, order.quantity_kwh)
        self.assertAlmostEqual(sum(t.quantity_kwh for t in trades), 1.25)


if __name__ == "__main__":
    unittest.main()
