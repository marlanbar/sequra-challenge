from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.operators.ecs import EcsOperator

# -----------------------------
# DAG defaults
# -----------------------------
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# -----------------------------
# Variables (configure in Airflow UI)
# -----------------------------
AIRBYTE_CONNECTION_ID = Variable.get("AIRBYTE_CONNECTION_ID")
RAW_BUCKET = Variable.get("RAW_BUCKET")
RAW_PREFIX = Variable.get("RAW_PREFIX", default_var="spacex/launches")

ECS_CLUSTER = Variable.get("ECS_CLUSTER")
ECS_TASK_DEFINITION = Variable.get("ECS_TASK_DEFINITION")
ECS_CONTAINER_NAME = Variable.get("ECS_CONTAINER_NAME", default_var="spacex-etl")
ECS_SUBNETS = Variable.get("ECS_SUBNETS", deserialize_json=True)
ECS_SECURITY_GROUPS = Variable.get("ECS_SECURITY_GROUPS", deserialize_json=True)

NETWORK_CONFIGURATION = {
    "awsvpcConfiguration": {
        "subnets": ECS_SUBNETS,
        "securityGroups": ECS_SECURITY_GROUPS,
        "assignPublicIp": "DISABLED",
    }
}

with DAG(
    dag_id="spacex_etl",
    default_args=default_args,
    description="ETL pipeline: Airbyte (EC2) -> S3 -> Redshift (COPY) -> dbt (Fargate)",
    schedule_interval="@monthly",
    catchup=False,
    max_active_runs=1,
    tags=["spacex", "airbyte", "redshift", "dbt", "fargate"],
) as dag:

    # Marker
    start = EmptyOperator(task_id="start")

    # 1) Trigger Airbyte sync via API (Airbyte server listens on port 8000)
    #    Requires an Airflow HTTP connection named 'airbyte_api' pointing to http://<EC2_PRIVATE_IP>:8000
    trigger_airbyte = SimpleHttpOperator(
        task_id="trigger_airbyte_sync",
        http_conn_id="airbyte_api",
        endpoint="/api/v1/connections/sync",
        method="POST",
        headers={"Content-Type": "application/json"},
        data={"connectionId": AIRBYTE_CONNECTION_ID},
        log_response=True,
    )

    # 2) Wait until raw data exists in S3
    #    We expect Airbyte to write to s3://<bucket>/<prefix>/<YYYY>/<MM>/<DD>/...
    wait_raw = S3KeySensor(
        task_id="wait_raw_data",
        bucket_name=RAW_BUCKET,
        bucket_key=f"{RAW_PREFIX}/{{{{ ds_nodash }}}}/*",
        wildcard_match=True,
        poke_interval=60,     # check every 60s
        timeout=60 * 30,      # up to 30 minutes
        mode="reschedule",    # free worker slot while waiting
        soft_fail=False,
    )

    # 3) Load from S3 to Redshift using our container (runs /app/etl.py)
    etl_load = EcsOperator(
        task_id="load_s3_to_redshift",
        aws_conn_id="aws_default",
        cluster=ECS_CLUSTER,
        task_definition=ECS_TASK_DEFINITION,
        launch_type="FARGATE",
        platform_version="LATEST",
        network_configuration=NETWORK_CONFIGURATION,
        propagate_tags="TASK_DEFINITION",
        overrides={
            "containerOverrides": [
                {"name": ECS_CONTAINER_NAME, "command": ["python", "/app/etl.py"]}
            ]
        },
    )

    # 4) Run dbt transformations (same image, different command)
    run_dbt = EcsOperator(
        task_id="run_dbt_models",
        aws_conn_id="aws_default",
        cluster=ECS_CLUSTER,
        task_definition=ECS_TASK_DEFINITION,
        launch_type="FARGATE",
        platform_version="LATEST",
        network_configuration=NETWORK_CONFIGURATION,
        propagate_tags="TASK_DEFINITION",
        overrides={
            "containerOverrides": [
                {"name": ECS_CONTAINER_NAME,
                 "command": ["bash", "-lc", "cd /app/dbt_project && dbt run"]},
            ]
        },
    )

    # 5) dbt tests to ensure data quality
    run_dbt_tests = EcsOperator(
        task_id="run_dbt_tests",
        aws_conn_id="aws_default",
        cluster=ECS_CLUSTER,
        task_definition=ECS_TASK_DEFINITION,
        launch_type="FARGATE",
        platform_version="LATEST",
        network_configuration=NETWORK_CONFIGURATION,
        propagate_tags="TASK_DEFINITION",
        overrides={
            "containerOverrides": [
                {"name": ECS_CONTAINER_NAME,
                 "command": ["bash", "-lc", "cd /app/dbt_project && dbt test"]},
            ]
        },
    )

    end = EmptyOperator(task_id="end")

    start >> trigger_airbyte >> wait_raw >> etl_load >> run_dbt >> run_dbt_tests >> end