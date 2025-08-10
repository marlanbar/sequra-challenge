#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ETL loader: COPY JSON from S3 into Redshift staging table.

- Expects env vars:
  RAW_BUCKET, RAW_PREFIX, AWS_REGION
  REDSHIFT_HOST, REDSHIFT_DB, REDSHIFT_USER, REDSHIFT_PASSWORD  (password auth)  OR
  REDSHIFT_HOST, REDSHIFT_DB, AWS_REGION, REDSHIFT_CLUSTER_ID    (IAM auth)
  EXEC_DATE (optional, YYYYMMDD) to select a specific partition/prefix

- Table: raw.spacex_launches (subset of fields; arrays like 'cores' are handled later by dbt)
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

RAW_BUCKET = os.environ["RAW_BUCKET"]
RAW_PREFIX = os.environ.get("RAW_PREFIX", "spacex/launches")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
EXEC_DATE = os.environ.get("EXEC_DATE")  # e.g., 20250810 from Airflow {{ ds_nodash }}

REDSHIFT_HOST = os.environ["REDSHIFT_HOST"]
REDSHIFT_DB = os.environ["REDSHIFT_DB"]

# Choose auth method:
USE_PASSWORD = "REDSHIFT_PASSWORD" in os.environ and "REDSHIFT_USER" in os.environ
REDSHIFT_USER = os.environ.get("REDSHIFT_USER")
REDSHIFT_PASSWORD = os.environ.get("REDSHIFT_PASSWORD")
REDSHIFT_CLUSTER_ID = os.environ.get("REDSHIFT_CLUSTER_ID")  # for IAM auth

# Optional: name of IAM role attached to the cluster allowing S3 read (preferred)
# If you attached a role, put its ARN here via env var; otherwise, leave empty and use ACCESS_KEY/SECRET via COPY CREDENTIALS.
REDSHIFT_IAM_ROLE_ARN = os.environ.get("REDSHIFT_IAM_ROLE_ARN", "")

def s3_path():
    """Build the S3 path to COPY from."""
    if EXEC_DATE:
        return f"s3://{RAW_BUCKET}/{RAW_PREFIX}/{EXEC_DATE}/"
    return f"s3://{RAW_BUCKET}/{RAW_PREFIX}/"

def connect_redshift():
    """Open a psycopg2 connection to Redshift."""
    dsn = {
        "host": REDSHIFT_HOST,
        "dbname": REDSHIFT_DB,
        "port": 5439,
        "sslmode": "prefer",
    }
    if USE_PASSWORD:
        dsn.update(user=REDSHIFT_USER, password=REDSHIFT_PASSWORD)
    else:
        # If using IAM auth via GetClusterCredentials, consider using redshift-connector package.
        # For simplicity here, assume password auth. You can switch to IAM later if desired.
        raise RuntimeError("Password auth expected. Provide REDSHIFT_USER and REDSHIFT_PASSWORD.")
    conn = psycopg2.connect(**dsn)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn

def ensure_table(cur):
    """Create a simple staging table if not exists (subset of JSON keys)."""
    cur.execute("""
        create schema if not exists raw;
        create table if not exists raw.spacex_launches (
            id         varchar(64),
            name       varchar(256),
            date_utc   varchar(64),
            date_unix  bigint,
            launchpad  varchar(64),
            success    boolean
        );
        truncate table raw.spacex_launches;
    """)

def copy_from_s3(cur):
    """COPY JSON data into staging table. Uses JSON 'auto' mapping by column names."""
    path = s3_path()
    # Prefer IAM role on the cluster (REDSHIFT_IAM_ROLE_ARN). If not available, you can switch to CREDENTIALS 'aws_access_key_id=...;aws_secret_access_key=...'
    if not REDSHIFT_IAM_ROLE_ARN:
        raise RuntimeError("Set REDSHIFT_IAM_ROLE_ARN to the role attached to the cluster with S3 read access.")
    copy_sql = f"""
        copy raw.spacex_launches
        from '{path}'
        region '{AWS_REGION}'
        format as json 'auto'
        timeformat 'auto'
        truncatecolumns
        compupdate off
        statupdate on
        maxerror 10
        iam_role '{REDSHIFT_IAM_ROLE_ARN}';
    """
    cur.execute(copy_sql)

def main():
    print(f"[etl] Starting COPY from {s3_path()} to raw.spacex_launches ...")
    with connect_redshift() as conn:
        with conn.cursor() as cur:
            ensure_table(cur)
            copy_from_s3(cur)
    print("[etl] COPY completed successfully.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[etl] ERROR: {e}", file=sys.stderr)
        raise