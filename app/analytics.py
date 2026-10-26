import json
import os
from collections import Counter
from datetime import datetime, timezone

import boto3


def calculate_analytics(events):
    """Calculate summary metrics from validated event records."""

    event_counts = Counter(event["event_type"] for event in events)

    unique_users = {
        event["user_id"]
        for event in events
    }

    purchases = [
        event
        for event in events
        if event["event_type"] == "purchase"
    ]

    failed_payments = event_counts.get("payment_failed", 0)

    total_purchase_value = round(
        sum(event["amount"] for event in purchases), 2
    )

    average_purchase_value = (
        round(total_purchase_value / len(purchases), 2)
        if purchases
        else 0.0
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_events": len(events),
        "event_counts": dict(sorted(event_counts.items())),
        "unique_users": len(unique_users),
        "successful_purchase_count": len(purchases),
        "total_purchase_value_pkr": total_purchase_value,
        "average_purchase_value_pkr": average_purchase_value,
        "failed_payment_count": failed_payments,
    }


def main():
    bucket_name = os.getenv("BUCKET_NAME")
    region = os.getenv("AWS_REGION", "us-east-1")
    source_key = os.getenv("SOURCE_KEY")

    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable is required")

    if not source_key:
        raise ValueError(
            "SOURCE_KEY must identify a processed JSONL file in S3"
        )

    s3 = boto3.client("s3", region_name=region)

    response = s3.get_object(
        Bucket=bucket_name,
        Key=source_key,
    )

    content = response["Body"].read().decode("utf-8")

    events = [
        json.loads(line)
        for line in content.splitlines()
        if line.strip()
    ]

    report = calculate_analytics(events)

    report_key = (
        "analytics/report-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + ".json"
    )

    s3.put_object(
        Bucket=bucket_name,
        Key=report_key,
        Body=json.dumps(report, indent=2).encode("utf-8"),
        ContentType="application/json",
    )

    print(json.dumps(report, indent=2))
    print(f"\nReport saved to s3://{bucket_name}/{report_key}")


if __name__ == "__main__":
    main()
