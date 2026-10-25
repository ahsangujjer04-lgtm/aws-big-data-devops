# AWS Big Data Pipeline with DevOps Automation

## Project Overview

A portfolio project demonstrating how to build and automate
a cloud-based data pipeline using AWS, Terraform, Python,
Docker, and GitHub Actions.

## Planned Architecture

1. Generate sample e-commerce events using Python.
2. Deliver events to Amazon S3 using Amazon Data Firehose.
3. Process and validate data using AWS Glue.
4. Query processed data using Amazon Athena.
5. Manage infrastructure using Terraform.
6. Automate testing and deployment using GitHub Actions.
7. Monitor resources using Amazon CloudWatch.

## Technologies

- Ubuntu Linux
- Git and GitHub
- Python
- Docker
- Terraform
- AWS IAM
- Amazon S3
- Amazon Data Firehose
- AWS Glue
- Amazon Athena
- Amazon CloudWatch
- GitHub Actions

## Project Status

Phase 1: Repository and development environment setup.

## Security

- Never commit AWS credentials or private keys.
- Use least-privilege IAM permissions.
- Prefer temporary credentials and GitHub Actions OIDC.
- Review AWS costs before deploying resources.
EOF
