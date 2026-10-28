import os

try:
    from .upload_to_s3 import upload_events
    from .process_events import process_s3_events
    from .analytics import generate_analytics_report
except ImportError:
    from upload_to_s3 import upload_events
    from process_events import process_s3_events
    from analytics import generate_analytics_report


def run_pipeline():
    """Run the complete S3 event processing and analytics pipeline."""

    bucket_name = os.getenv("BUCKET_NAME")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable is required")

    print("\n" + "=" * 60)
    print("STARTING AWS BIG DATA PIPELINE")
    print("=" * 60)

    # Stage 1: Generate events and upload them to S3.
    print("\n[1/3] Uploading raw events...")
    raw_key = upload_events()

    # Stage 2: Validate and process the uploaded events.
    print("\n[2/3] Processing raw events...")
    processing_result = process_s3_events(
        bucket_name=bucket_name,
        source_key=raw_key,
        region=region,
    )

    # Stage 3: Generate analytics when there are valid records.
    processed_key = processing_result["processed_key"]

    report_result = None

    if processed_key:
        print("\n[3/3] Generating analytics report...")
        report_result = generate_analytics_report(
            bucket_name=bucket_name,
            source_key=processed_key,
            region=region,
        )
    else:
        print("\n[3/3] Skipping analytics: no valid events were produced.")

    # Print the final execution summary.
    summary = {
        "raw_key": raw_key,
        "processed_key": processed_key,
        "rejected_key": processing_result["rejected_key"],
        "input_count": processing_result["input_count"],
        "valid_count": processing_result["valid_count"],
        "rejected_count": processing_result["rejected_count"],
        "report_key": (
            report_result["report_key"] if report_result else None
        ),
    }

    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("\nPipeline completed successfully!")

    return summary


if __name__ == "__main__":
    run_pipeline()
