import json
import random
import uuid
from datetime import datetime, timezone


EVENT_TYPES = [
    "product_view",
    "add_to_cart",
    "purchase",
    "payment_failed",
]

PRODUCT_IDS = [
    "product-101",
    "product-102",
    "product-103",
    "product-104",
]


def generate_event():
    """Generate one simulated e-commerce event."""

    return {
        "event_id": str(uuid.uuid4()),
        "event_type": random.choice(EVENT_TYPES),
        "user_id": f"user-{random.randint(100, 999)}",
        "product_id": random.choice(PRODUCT_IDS),
        "amount": round(random.uniform(100, 5000), 2),
        "currency": "PKR",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    """Generate five sample e-commerce events."""

    for _ in range(5):
        event = generate_event()
        print(json.dumps(event))


if __name__ == "__main__":
    main()
