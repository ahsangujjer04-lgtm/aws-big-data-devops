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
    """Return (is_valid, reason) for an event."""

    if not isinstance(event, dict):
        return False, "Event must be a JSON object"

    missing_fields = REQUIRED_FIELDS - event.keys()
    if missing_fields:
        return False, f"Missing fields: {', '.join(sorted(missing_fields))}"

    if not isinstance(event["event_id"], str) or not event["event_id"].strip():
        return False, "event_id must be a non-empty string"

    if event["event_type"] not in VALID_EVENT_TYPES:
        return False, "Invalid event_type"

    if not isinstance(event["user_id"], str) or not event["user_id"].strip():
        return False, "user_id must be a non-empty string"

    if not isinstance(event["product_id"], str) or not event["product_id"].strip():
        return False, "product_id must be a non-empty string"

    if (
        isinstance(event["amount"], bool)
        or not isinstance(event["amount"], (int, float))
        or event["amount"] < 0
    ):
        return False, "amount must be a non-negative number"

    if not isinstance(event["currency"], str) or not event["currency"].strip():
        return False, "currency must be a non-empty string"

    try:
        datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError):
        return False, "timestamp must be a valid ISO 8601 timestamp"

    return True, "Valid"


def process_events(events):
    """Separate valid events from rejected records."""

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
    """Read JSON Lines from an S3 object."""

    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    content = response["Body"].read().decode("utf-8")

    events = []

    for line_number, line in enumerate(content.splitlines(), start=1):
        if not line.strip():
            continue

        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append(None)

    return events


def upload_jsonl(s3, bucket_name, object_key, records):
    """Upload records as JSON Lines."""

    content = "".join(
        json.dumps(record, ensure_ascii=False) + "\n"
        for record in records
    )

    s3.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=content.encode("utf-8"),
        ContentType="application/x-ndjson",
    )


def main():
    bucket_name = os.getenv("BUCKET_NAME")
    region = os.getenv("AWS_REGION", "us-east-1")
    source_key = os.getenv("SOURCE_KEY")

    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable is required")

    if not source_key:
        raise ValueError(
            "SOURCE_KEY is required, for example raw/events-20261026T094547Z.jsonl"
        )

    s3 = boto3.client("s3", region_name=region)

    events = read_s3_events(s3, bucket_name, source_key)
    valid_events, rejected_events = process_events(events)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

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


if __name__ == "__main__":
    main()
