terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

variable "aws_region" {
  description = "AWS region where the S3 bucket will be created"
  type        = string
  default     = "us-east-1"
}

provider "aws" {
  region = var.aws_region
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "events" {
  bucket = "aws-big-data-devops-events-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "aws-big-data-devops-events"
    Environment = "dev"
    ManagedBy   = "Terraform"
    Project     = "aws-big-data-devops"
  }
}

resource "aws_s3_bucket_public_access_block" "events" {
  bucket = aws_s3_bucket.events.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "events" {
  bucket = aws_s3_bucket.events.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

output "bucket_name" {
  description = "Name of the S3 bucket for event data"
  value       = aws_s3_bucket.events.bucket
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.events.arn
}
