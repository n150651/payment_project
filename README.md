🏦 High-Volume Transaction & Fraud Analysis Platform
A distributed financial data platform designed to process real-time transactions and perform asynchronous fraud detection using MySQL Replication and Apache Airflow.

🚀 Project Overview
This project simulates a production-grade banking environment. It decouples OLTP (Online Transaction Processing) from OLAP (Online Analytical Processing) to ensure system stability under high load.

Real-time Layer: A Python API (FastAPI) handles incoming transactions and writes to a Primary MySQL Database.

Reliability Layer: A Read-Replica syncs data in real-time using GTID-based replication, ensuring data redundancy.

Analytical Layer: Apache Airflow runs nightly batch jobs against the Replica (to avoid locking the Primary) to identify fraud patterns and generate compliance reports.

🛠️ Tech StackLanguage: Python 3.12 (FastAPI, PyMySQL)Database: MySQL 8.0 (Master-Slave Replication Cluster)Orchestration: Apache Airflow 2.10 (running on Docker)Containerization: Docker & Docker ComposeScripting: Bash (Automated infrastructure provisioning)⚙️ Setup & Installation1. PrerequisitesDocker & Docker Compose installed.(Windows Users) WSL 2 configured with at least 6GB RAM.2. Environment ConfigurationCreate a .env file in the root directory:Ini, TOML# Database Secrets
MYSQL_ROOT_PASSWORD=rootpassword
REPLICA_USER=app_user
REPLICA_PASSWORD=AppPass123!
REPL_USER=repl_user
REPL_PASSWORD=ReplicaPass123!

# Airflow Secrets
AIRFLOW_DB_USER=airflow
AIRFLOW_DB_PASS=airflow
AIRFLOW_UID=1000
3. One-Click InitializationUse the automated reset script to provision the entire stack, configure replication, and initialize Airflow.Bashchmod +x reset_db.sh
./reset_db.sh
🖥️ Access PointsServiceURL / PortCredentialsDescriptionTransaction APIhttp://localhost:8000/docsN/ASwagger UI to post transactionsAirflow UIhttp://localhost:8080admin / adminETL Orchestration DashboardMySQL Sourcelocalhost:3306root / rootpasswordPrimary DB (Writes)MySQL Replicalocalhost:3307app_user / AppPass123!Read-Only DB (Analytics)🧪 Testing the PipelineScenario: Detecting a Fraudulent TransactionThe system automatically flags any transaction over $10,000 USD.1. Inject Data (OLTP)Go to the API Docs and POST a high-value transaction:JSON{
  "user_id": 999,
  "amount": 15000.00,
  "currency": "USD"
}
2. Trigger Analysis (OLAP)Login to Airflow.Trigger the DAG: 02_fraud_analysis_etl.Wait for the task to complete (Dark Green).3. Verify OutputCheck the generated report in the logs:Bashcat airflow/logs/fraud_reports/fraud_report_*.csv
Expected Output:Code snippetTransaction ID,User ID,Amount,Currency,Status
1,999,15000.00,USD,FLAGGED_FRAUD

📊 Monitoring & Observability
The platform includes a full observability stack to track system health and transaction throughput.

1. Architecture
Prometheus: Scrapes metrics from MySQL every 15s.

MySQL Exporter: Exposes internal DB metrics (Connections, Queries, Replication Lag).

Grafana: Visualizes the data.

2. Accessing the Dashboard
URL: http://localhost:3000

Credentials: admin / admin

Setup:

Add Data Source: Prometheus (URL: http://prometheus:9090).

Import Dashboard ID: 7362 (MySQL Overview).

3. Performance Load Testing
To validate system stability, use the included Python load generator scripts.

Run a Stress Test (10 Concurrent Threads):

Bash

python3 heavy_load.py
Typical Result: ~150 TPS (Transactions Per Second) on a standard dev machine.

Observation: Monitor the "MySQL Questions" graph in Grafana to see the real-time traffic spike.

# High-Volume Transaction & Fraud Analysis Platform (Optimized)

A high-performance financial data platform designed for sub-second transaction processing and asynchronous fraud detection.

## 🚀 Performance Benchmarks
* **Throughput:** ~156 Transactions Per Second (TPS)
* **Daily Capacity:** ~13.4 Million Transactions
* **Avg Latency:** 318ms (at peak load)
* **Concurrency:** 50+ simultaneous virtual users

## 🛠️ "Real-Time" System Design Choices

### 1. Asynchronous I/O (The Python Layer)
We refactored the core FastAPI application from synchronous to **Asynchronous (AsyncIO)**.
* **Benefit:** Utilizes an Event Loop to handle I/O-bound database operations. The server no longer "freezes" while waiting for MySQL disk writes.
* **Process Management:** Deployed via **Gunicorn with Uvicorn workers** to utilize all available CPU cores.

### 2. DBA Optimization (The Storage Layer)
The MySQL engine was tuned for high-volume writes rather than standard out-of-the-box defaults:
* **Connection Pooling:** Implemented via SQLAlchemy `AsyncSession` to reuse database handles and prevent handshake overhead.
* **InnoDB Buffer Pool:** Allocated **1GB RAM** to ensure indexes and active data stay in memory.
* **Write Buffering:** Set `innodb_flush_log_at_trx_commit = 2`, increasing write throughput by ~5x by leveraging OS-level caching.

### 3. Decoupled Architecture (OLTP vs OLAP)
To maintain real-time speed, we separated traffic:
* **Writes:** Directed to the **Source/Master DB**.
* **Reads/Analytics:** Directed to the **GTID-based Replica**.
* **Airflow ETL:** Fraud analysis DAGs use **Pandas Batching** on the Replica to prevent locking the Master during heavy computation.

### 4. Observability & Security
* **Monitoring:** Prometheus scrapes the FastAPI `/metrics` endpoint and MySQL Exporter. Visualized in **Grafana** to track "Replication Lag" and "API Latency."
* **Security:** Implemented **X-API-KEY** header validation to prevent unauthorized Database DoS attacks.