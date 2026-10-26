import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from process_events import process_events, validate_event


def make_valid_event():
    return {
        "event_id": "event-001",
        "event_type": "purchase",
        "user_id": "user-001",
        "product_id": "product-001",
        "amount": 1500.50,
        "currency": "PKR",
        "timestamp": "2026-10-26T09:00:00+00:00",
    }


class TestValidateEvent(unittest.TestCase):

    def test_valid_event(self):
        valid, reason = validate_event(make_valid_event())
        self.assertTrue(valid)
        self.assertEqual(reason, "Valid")

    def test_missing_event_id(self):
        event = make_valid_event()
        del event["event_id"]

        valid, reason = validate_event(event)

        self.assertFalse(valid)
        self.assertIn("Missing fields", reason)

    def test_invalid_event_type(self):
        event = make_valid_event()
        event["event_type"] = "unknown_event"

        valid, reason = validate_event(event)

        self.assertFalse(valid)
        self.assertEqual(reason, "Invalid event_type")

    def test_negative_amount(self):
        event = make_valid_event()
        event["amount"] = -100

        valid, reason = validate_event(event)

        self.assertFalse(valid)
        self.assertIn("non-negative", reason)

    def test_missing_user_id(self):
        event = make_valid_event()
        del event["user_id"]

        valid, reason = validate_event(event)

        self.assertFalse(valid)
        self.assertIn("Missing fields", reason)

    def test_process_events_separates_valid_and_invalid(self):
        valid_event = make_valid_event()
        invalid_event = make_valid_event()
        invalid_event["event_type"] = "unknown_event"

        valid_events, rejected_events = process_events(
            [valid_event, invalid_event]
        )

        self.assertEqual(len(valid_events), 1)
        self.assertEqual(len(rejected_events), 1)
        self.assertEqual(
            rejected_events[0]["reason"],
            "Invalid event_type",
        )


if __name__ == "__main__":
    unittest.main()
