import unittest
from datetime import date
from period_tracker.logic import (
    cycle_lengths,
    period_lengths,
    avg_cyc,
    avg_period,
    analyse,
    predict,
    forecast_windows,
)


class TestLogicModule(unittest.TestCase):
    def setUp(self):
        self.dates = [date(2024, 5, 1), date(2024, 5, 30), date(2024, 6, 28)]
        self.entries = [
            {"start": "2024-05-01", "end": "2024-05-05"},
            {"start": "2024-05-30", "end": "2024-06-03"},
            {"start": "2024-06-28", "end": "2024-07-02"},
        ]

    def test_cycle_lengths(self):
        self.assertEqual(cycle_lengths(self.dates), [29, 29])

    def test_period_lengths(self):
        self.assertEqual(period_lengths(self.entries), [5, 5, 5])

    def test_avg_cyc(self):
        self.assertEqual(avg_cyc(self.dates), 29)

    def test_avg_period(self):
        self.assertEqual(avg_period(self.entries), 5)

    def test_analyse(self):
        result = analyse(self.entries)
        self.assertEqual(result["avg"], 29.0)
        self.assertEqual(result["min"], 29)
        self.assertEqual(result["max"], 29)
        self.assertIsNone(result["std_dev"])

    def test_predict(self):
        avg, next_period, fertile, last = predict(self.entries)
        self.assertEqual(avg, 29)
        self.assertEqual(last, date(2024, 6, 28))
        self.assertEqual(next_period, date(2024, 7, 27))
        self.assertEqual(fertile[0], date(2024, 7, 11))
        self.assertEqual(fertile[1], date(2024, 7, 15))

    def test_forecast_windows(self):
        future = forecast_windows(date(2024, 6, 1), 28, count=2)
        self.assertEqual(len(future), 2)
        self.assertEqual(future[0]["next_period"], date(2024, 6, 29))
        self.assertEqual(future[1]["next_period"], date(2024, 7, 27))
