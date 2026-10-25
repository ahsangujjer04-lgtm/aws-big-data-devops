import unittest

from app.producer import generate_event


class TestProducer(unittest.TestCase):

    def test_event_has_required_fields(self):
        event = generate_event()

        required_fields = {
            "event_id",
            "event_type",
            "user_id",
            "product_id",
            "amount",
            "currency",
            "timestamp",
        }

        self.assertTrue(required_fields.issubset(event.keys()))

    def test_event_has_valid_type(self):
        event = generate_event()

        valid_types = {
            "product_view",
            "add_to_cart",
            "purchase",
            "payment_failed",
        }

        self.assertIn(event["event_type"], valid_types)

    def test_amount_is_positive(self):
        event = generate_event()

        self.assertGreater(event["amount"], 0)


if __name__ == "__main__":
    unittest.main()
