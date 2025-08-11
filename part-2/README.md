# Part 2 — Orchestration & Containers

## Overview
This section describes the orchestration and containerization approach for the seQura Senior Data Engineer challenge. The goal is to run ETL and transformation tasks in a portable, reproducible environment while orchestrating their execution using AWS Managed Workflows for Apache Airflow (MWAA).

---

## Architecture

- **MWAA** is used to schedule and monitor all pipeline tasks.
- The ETL and transformation logic (e.g., `etl.py`, dbt models) are packaged in a Docker image.
- The Docker image is stored in Amazon Elastic Container Registry (ECR) and run on AWS ECS Fargate tasks triggered by Airflow.
- Airflow DAGs reference ECS tasks via the `EcsOperator` to execute scripts inside the container.

---


### Why Airbyte runs on EC2 and ETL/dbt on Fargate

In this challenge, Airbyte is deployed on EC2 instead of Fargate because it is a persistent multi-container service (server, scheduler, database, and webapp) that needs to run 24/7. EC2 with Docker Compose allows hosting all these containers together on a single host, simplifying networking and resource sharing, and reducing cost compared to keeping multiple Fargate tasks running continuously.

In contrast, the ETL and dbt processes are short-lived, stateless jobs. AWS Fargate is ideal for this type of workload because it scales to zero when not running, requires no server management, and allows fine-grained CPU/memory allocation per task. MWAA triggers these Fargate tasks via the `EcsOperator` only when needed, ensuring cost efficiency and operational simplicity.

---

## Docker Image

The Docker image includes:
- Python 3.11
- Required Python libraries for the ETL (`pandas`, `boto3`, `sqlalchemy`, `psycopg2-binary`, `requests`, etc.).
- The ETL script (`etl.py`) and dbt project files.

---

## Airflow Orchestration (MWAA)

- **DAG Structure:**
  1. Trigger Airbyte task to download data to S3.
  1. Trigger ECS task to run the ETL script (`etl.py`) which loads data from S3 into Redshift.
  2. Trigger ECS task to run dbt transformations inside Redshift.
- The DAGs are stored in S3 and automatically picked up by MWAA.
- Task retries, SLAs, and dependencies are managed in Airflow.

---

## Monitoring & Logging
- ECS task logs are sent to Amazon CloudWatch for debugging and audit purposes.
- MWAA provides native Airflow UI for monitoring DAG execution status and task logs.

---

## Files in this folder
- `Dockerfile` — Docker image definition for ETL/dbt execution.
- `requirements.txt` — Python dependencies for the container.
- `README.md` — This documentation.

---
