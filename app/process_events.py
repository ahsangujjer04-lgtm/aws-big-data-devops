import json
import os
from datetime import datetime, timezone

import boto3


REQUIRED_FIELDS = {
    "event_id",
    "event_type",
    "user_id",
    "product_id",
    "amount",
    "currency",
    "timestamp",
}

VALID_EVENT_TYPES = {
    "product_view",
    "add_to_cart",
    "purchase",
    "payment_failed",
}


def validate_event(event):
    """Validate a single event and return (is_valid, reason)."""

    if not isinstance(event, dict):
        return False, "Event must be a JSON object"

    missing_fields = REQUIRED_FIELDS - event.keys()
    if missing_fields:
        return False, f"Missing fields: {', '.join(sorted(missing_fields))}"

    for field in ("event_id", "user_id", "product_id", "currency"):
        if not isinstance(event[field], str) or not event[field].strip():
            return False, f"{field} must be a non-empty string"

    if event["event_type"] not in VALID_EVENT_TYPES:
        return False, "Invalid event_type"

    amount = event["amount"]
    if (
        isinstance(amount, bool)
        or not isinstance(amount, (int, float))
        or amount < 0
    ):
        return False, "amount must be a non-negative number"

    if isinstance(amount, float) and not __import__("math").isfinite(amount):
        return False, "amount must be finite"

    try:
        datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
    except (ValueError, AttributeError, TypeError):
        return False, "Invalid timestamp"

    return True, "Valid"


def process_events(events):
    """Separate valid events from rejected events."""

    valid_events = []
    rejected_events = []

    for line_number, event in enumerate(events, start=1):
        is_valid, reason = validate_event(event)

        if is_valid:
            valid_events.append(event)
        else:
            rejected_events.append({
                "line_number": line_number,
                "reason": reason,
                "record": event,
            })

    return valid_events, rejected_events


def read_s3_events(s3, bucket_name, object_key):
    """Read JSON Lines events from an S3 object."""

    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    content = response["Body"].read().decode("utf-8")

    events = []

    for line in content.splitlines():
        if not line.strip():
            continue

        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append(None)

    return events


def upload_jsonl(s3, bucket_name, object_key, records):
    """Upload records to S3 in JSON Lines format."""

    content = "\n".join(
        json.dumps(record, ensure_ascii=False) for record in records
    ) + "\n"

    s3.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=content.encode("utf-8"),
        ContentType="application/x-ndjson",
    )


def process_s3_events(bucket_name, source_key, region="us-east-1"):
    """Process an S3 object and return output keys and record counts."""

    if not bucket_name:
        raise ValueError("bucket_name is required")

    if not source_key:
        raise ValueError("source_key is required")

    s3 = boto3.client("s3", region_name=region)

    events = read_s3_events(s3, bucket_name, source_key)
    valid_events, rejected_events = process_events(events)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

    processed_key = None
    rejected_key = None

    if valid_events:
        processed_key = f"processed/events-{timestamp}.jsonl"
        upload_jsonl(s3, bucket_name, processed_key, valid_events)
        print(f"Processed data: s3://{bucket_name}/{processed_key}")
    else:
        print("No valid events to upload.")

    if rejected_events:
        rejected_key = f"rejected/events-{timestamp}.jsonl"
        upload_jsonl(s3, bucket_name, rejected_key, rejected_events)
        print(f"Rejected data: s3://{bucket_name}/{rejected_key}")
    else:
        print("No rejected events.")

    print(f"Input records: {len(events)}")
    print(f"Valid records: {len(valid_events)}")
    print(f"Rejected records: {len(rejected_events)}")

    return {
        "processed_key": processed_key,
        "rejected_key": rejected_key,
        "input_count": len(events),
        "valid_count": len(valid_events),
        "rejected_count": len(rejected_events),
    }


def main():
    bucket_name = os.getenv("BUCKET_NAME")
    region = os.getenv("AWS_REGION", "us-east-1")
    source_key = os.getenv("SOURCE_KEY")

    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable is required")

    if not source_key:
        raise ValueError(
            "SOURCE_KEY is required, for example raw/events-example.jsonl"
        )

    process_s3_events(bucket_name, source_key, region)


if __name__ == "__main__":
    main()
