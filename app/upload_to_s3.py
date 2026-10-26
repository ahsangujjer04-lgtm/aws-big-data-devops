import json
import os
from datetime import datetime, timezone

import boto3

from producer import generate_event


def upload_events():
    """Generate sample events and upload them to Amazon S3."""

    bucket_name = os.getenv("BUCKET_NAME")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not bucket_name:
        raise ValueError(
            "BUCKET_NAME is not set. Please configure your S3 bucket name."
        )

    # Generate five events in JSON Lines format.
    events = [generate_event() for _ in range(5)]

    content = "\n".join(json.dumps(event) for event in events) + "\n"

    # Generate a unique object key for each upload.
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    object_key = f"raw/events-{timestamp}.jsonl"

    s3 = boto3.client("s3", region_name=region)

    s3.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=content.encode("utf-8"),
        ContentType="application/x-ndjson",
    )

    print(f"Successfully uploaded {len(events)} events.")
    print(f"Bucket: {bucket_name}")
    print(f"Object key: {object_key}")
    print(f"S3 URI: s3://{bucket_name}/{object_key}")


if __name__ == "__main__":
    upload_events()
