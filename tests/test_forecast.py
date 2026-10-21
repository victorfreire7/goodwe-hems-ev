"""Testes das previsões de geração solar."""
import unittest
from datetime import datetime, timedelta

from engine.forecast import persistence, same_hour_average


def daily_profile(days):
    """Mesma curva todos os dias: o previsor por média da mesma hora tem de acertar exatamente."""
    start = datetime(2026, 1, 1)
    profile = {}
    for index in range(24 * days):
        hour = start + timedelta(hours=index)
        profile[hour] = max(0, (hour.hour - 6) * (18 - hour.hour)) / 100
    return profile


class ForecastTests(unittest.TestCase):
    def test_same_hour_average_is_exact_on_a_repeating_day(self):
        profile = daily_profile(10)
        hour = datetime(2026, 1, 9, 12)
        self.assertAlmostEqual(same_hour_average(profile, hour), profile[hour])

    def test_same_hour_average_needs_seven_days_of_history(self):
        self.assertIsNone(same_hour_average(daily_profile(10), datetime(2026, 1, 5, 12)))

    def test_persistence_uses_the_previous_hour(self):
        profile = daily_profile(2)
        hour = datetime(2026, 1, 2, 12)
        self.assertEqual(persistence(profile, hour), profile[hour - timedelta(hours=1)])


if __name__ == "__main__":
    unittest.main()
