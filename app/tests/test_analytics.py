import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analytics import calculate_analytics


class TestCalculateAnalytics(unittest.TestCase):

    def setUp(self):
        self.events = [
            {
                "event_type": "product_view",
                "user_id": "user_1",
                "amount": 0
            },
            {
                "event_type": "purchase",
                "user_id": "user_1",
                "amount": 1500
            },
            {
                "event_type": "payment_failed",
                "user_id": "user_2",
                "amount": 500
            },
            {
                "event_type": "purchase",
                "user_id": "user_3",
                "amount": 2500
            },
            {
                "event_type": "payment_failed",
                "user_id": "user_2",
                "amount": 300
            }
        ]

    def test_total_events(self):
        report = calculate_analytics(self.events)
        self.assertEqual(report["total_events"], 5)

    def test_event_counts(self):
        report = calculate_analytics(self.events)

        self.assertEqual(
            report["event_counts"],
            {
                "payment_failed": 2,
                "product_view": 1,
                "purchase": 2
            }
        )

    def test_unique_users(self):
        report = calculate_analytics(self.events)
        self.assertEqual(report["unique_users"], 3)

    def test_successful_purchase_count(self):
        report = calculate_analytics(self.events)
        self.assertEqual(report["successful_purchase_count"], 2)

    def test_total_purchase_value(self):
        report = calculate_analytics(self.events)
        self.assertEqual(report["total_purchase_value_pkr"], 4000)

    def test_average_purchase_value(self):
        report = calculate_analytics(self.events)
        self.assertEqual(report["average_purchase_value_pkr"], 2000)

    def test_failed_payment_count(self):
        report = calculate_analytics(self.events)
        self.assertEqual(report["failed_payment_count"], 2)

    def test_empty_events(self):
        report = calculate_analytics([])

        self.assertEqual(report["total_events"], 0)
        self.assertEqual(report["unique_users"], 0)
        self.assertEqual(report["successful_purchase_count"], 0)
        self.assertEqual(report["total_purchase_value_pkr"], 0)
        self.assertEqual(report["average_purchase_value_pkr"], 0.0)
        self.assertEqual(report["failed_payment_count"], 0)


if __name__ == "__main__":
    unittest.main()
