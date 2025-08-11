# seQura Data Engineer Coding Challenge

## Overview

This repository contains the solution for the seQura Senior Data Engineer Technical Test.

The challenge consists of designing a scalable data architecture on AWS, building an end-to-end data ingestion pipeline using containerized processes and orchestration tools, and performing analytical queries on SpaceX launch data.

---

## 📦 Deliverables

### 1. **Data Infrastructure on AWS**
- A scalable and secure architecture diagram.
- Terraform code to provision an Amazon Redshift cluster.
- Documentation on:
  - Storage and processing design choices.
  - Security and access control strategy.

### 2. **Orchestration & Containers**
- Dockerized ETL pipeline.
- Airflow DAG to schedule and monitor the pipeline.

### 3. **ETL Pipeline**
- Python script to extract, transform, and load SpaceX launch data from the provided JSON file.
- dbt models for data transformations.
- Explanation of how the ETL pipeline is scheduled and monitored using Airflow.

### 4. **SQL Queries**
- Query 1: What is the maximum number of times a core has been reused?
- Query 2: List the cores that were reused in less than 50 days since their previous launch.

---

## ❓ Discussion Questions

### 1. Design Decisions
- Why did you choose the specific tools for data extraction?
- What are the pros and cons of using AWS S3 as staging storage?
- How does Amazon Redshift fit into the overall architecture and what are its key advantages for this use case?

### 2. Scalability & Performance
- How does your architecture scale with increasing data volume?
- What are the potential bottlenecks and how would you resolve them?
- How can the ETL pipeline be optimized?

### 3. Data Quality & Testing
- How do you ensure data quality and integrity across the pipeline?
- What types of tests are implemented?
- How do you manage schema changes in the source data?

### 4. Orchestration & Monitoring
- How does Airflow support observability and retry mechanisms?
- How would you handle pipeline failures?

---

## 📁 Structure

```
├── part-1/               # Data Infrastructure on AWS (architecture, Terraform, security docs)
├── part-2/               # Orchestration & Containers (Docker setup, Airflow DAGs)
├── part-3/               # ETL Pipeline (JSON ingestion, transformations)
├── part-4/               # SQL Queries (analysis of SpaceX core reuse)
└── README.md             # This documentation
```