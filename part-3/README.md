# SpaceX Data ETL Pipeline - Part 3 - ETL Pipeline

## Overview
This part of the challenge focuses on implementing an ETL pipeline using Airbyte for data extraction from the SpaceX API and Python scripts for transforming and loading the data into Amazon Redshift. 
Further transformations, modeling and testing are handled using dbt (Data Build Tool). The entire process is orchestrated using Amazon Managed Workflows for Apache Airflow (MWAA). 
The scripts and models used are located in the airflow/, dbt/ and scripts/ folders.

## Components

1. **Airbyte**: Used for extracting data from the SpaceX API and loading raw data into AWS S3.
2. **Python Script**: Used for transforming and loading data from S3 into Amazon Redshift.
3. **Amazon Redshift**: Data warehouse where transformed data is stored for analytics.
4. **dbt (Data Build Tool)**: Performs data transformations within Redshift and ensures data quality through testing.
5. **Amazon Managed Workflows for Apache Airflow (MWAA)**: Orchestrates the ETL process.

### Prerequisites

- AWS account with necessary permissions.
- Airbyte installed and configured on an EC2 instance in public subnet of VPC.
- Redshift cluster set up with a database and table.
- Airflow environment set up using Amazon Managed Workflows for Apache Airflow (MWAA).
- dbt available in the same ECS Fargate container that runs the ETL script.

### Step-by-Step Guide

The overall flow is Airbyte (EC2, public subnet) → S3 → ECS Fargate (`etl.py` & dbt) → Redshift.

1. Configure Airbyte:
	-   Access the Airbyte web interface.
	-   Set up a new source to extract data from the SpaceX API.
	-   Set up a new destination to load data into the S3 bucket.

2. Transform and Load Data Using Python Script
    -   The Python script (scripts/etl.py) is run within ECS Fargate as part of the Airflow DAG to read data from S3, transform it, and load it into Redshift.

3. Use dbt Models
    -   The dbt models (e.g., src_spacex_launches.sql and spacex_launches.sql in the models directory) are also run within ECS Fargate via Airflow. These models define transformation logic to clean and transform the data with incremental updates. 
        
4. Orchestrate with Airflow
    -   Copy the DAG file (airflow/spacex_etl_dag.py) to orchestrate the ETL process, including running the Airbyte extraction and the Python transformation/loading script. This dag can be set up to be run daily or monthly depending on the team's needs.

### Running the ETL Pipeline

1.	Deploy Airflow DAG:
	•	Deploy the spacex_etl_dag.py file to your Airflow environment.
2.	Run the Pipeline:
	•	Trigger the Airflow DAG to start the ETL process.
	•	Monitor the DAG execution in the Airflow web interface.

### Incremental Updates with dbt

By configuring dbt models with incremental logic, each run of the DAG will only update the models with new or updated data. 
This approach is efficient for large datasets, ensuring that only necessary data is processed.

### Design Decisions

Airbyte runs on EC2 for easy setup and control over connectors. ETL and dbt run in ECS Fargate for isolation, scalability, and avoiding EC2 management overhead. Redshift is deployed in a private subnet for security, accessed only from within the VPC.
