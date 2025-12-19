#!/bin/bash

# --- 1. LOAD SECRETS ---
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "❌ Error: .env file not found!"
  exit 1
fi

echo "🔑 Loaded secrets from .env"

# --- 1.5 SETUP FOLDERS ---
echo "🔧 Creating Airflow folders..."
mkdir -p airflow/dags airflow/logs airflow/plugins

# --- 2. CLEAN & START ---
echo "💥 Nuke and Pave..."
docker-compose down
# Using sudo to ensure we delete root-owned DB files
sudo rm -rf mysql_replication/data/source/*
sudo rm -rf mysql_replication/data/replica/*

echo "🚀 Starting containers..."
docker-compose up -d

echo "⏳ Waiting 30s for database wake-up..."
sleep 30

# --- 3. CONFIGURE SOURCE (All Users & Data) ---
# DBA NOTE: We create ALL users on Source. They will replicate to Replica automatically.
echo "🛠 Configuring Source Database..."
docker exec -i mysql-source mysql -uroot -p${MYSQL_ROOT_PASSWORD} <<EOF
-- A. Create Replication User
CREATE USER IF NOT EXISTS '${REPL_USER}'@'%' IDENTIFIED BY '${REPL_PASSWORD}';
GRANT REPLICATION SLAVE ON *.* TO '${REPL_USER}'@'%';

-- B. Create Airflow Metadata DB & User
CREATE DATABASE IF NOT EXISTS airflow_metadata;
CREATE USER IF NOT EXISTS '${AIRFLOW_DB_USER}'@'%' IDENTIFIED BY '${AIRFLOW_DB_PASS}';
GRANT ALL PRIVILEGES ON airflow_metadata.* TO '${AIRFLOW_DB_USER}'@'%';

-- C. Create Metrics Exporter User
CREATE USER IF NOT EXISTS '${METRICS_USER}'@'%' IDENTIFIED BY '${METRICS_PASSWORD}';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO '${METRICS_USER}'@'%';
GRANT SELECT ON performance_schema.* TO '${METRICS_USER}'@'%';

-- D. Create App User (This will replicate to the Slave!)
CREATE USER IF NOT EXISTS '${REPLICA_USER}'@'%' IDENTIFIED BY '${REPLICA_PASSWORD}';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE ON payment_db.* TO '${REPLICA_USER}'@'%';

FLUSH PRIVILEGES;
EOF

# --- 4. CONFIGURE REPLICA ---
echo "🔗 Linking Replica..."
docker exec -i mysql-replica mysql -uroot -p${MYSQL_ROOT_PASSWORD} <<EOF
STOP REPLICA;
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST = 'mysql-source',
  SOURCE_USER = '${REPL_USER}',
  SOURCE_PASSWORD = '${REPL_PASSWORD}',
  SOURCE_AUTO_POSITION = 1;
START REPLICA;
EOF

# (Deleted old Section 5 because we moved it to Source)

# --- 6. INITIALIZE AIRFLOW ---
echo "💨 Running Airflow Migrations (This takes ~60 seconds)..."
docker-compose run --rm airflow-webserver airflow db migrate

echo "👤 Creating Airflow Admin User..."
docker-compose run --rm airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# --- 7. VERIFY ---
echo "✅ Status Check:"
docker exec -it mysql-replica mysql -uroot -p${MYSQL_ROOT_PASSWORD} -e "SHOW REPLICA STATUS\G" | grep "Running: Yes"
echo "✅ Airflow is ready at http://localhost:8080 (User: admin / Pass: admin)"