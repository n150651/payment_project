#!/bin/bash

echo "🚀 Starting High-Performance Payment Stack Reset..."

# 1. Stop and remove existing containers/volumes
docker-compose down -v

# 2. Build and start MySQL services first
docker-compose up -d mysql-source mysql-replica
echo "⏳ Waiting for MySQL Source to be healthy..."

# Loop until mysql-source is healthy
until [ "`docker inspect -f {{.State.Health.Status}} mysql-source`"=="healthy" ]; do
    sleep 2
done

echo "✅ MySQL Source is UP. Configuring Replication..."

# 3. Automatic Replication Handshake (GTID Based)
# We get the Master status and apply it to the Replica
docker exec -it mysql-replica mysql -uroot -prootpassword -e "
STOP SLAVE;
CHANGE MASTER TO 
    MASTER_HOST='mysql-source', 
    MASTER_USER='repl_user', 
    MASTER_PASSWORD='ReplicaPass123!', 
    MASTER_AUTO_POSITION=1;
START SLAVE;"

echo "✅ Replication Link established."

# 4. Initialize Airflow Database
echo "init Airflow..."
docker-compose up -d airflow-webserver airflow-scheduler

# 5. Start the Payment API and Monitoring
docker-compose up -d payment-app prometheus grafana mysql-exporter

echo "-------------------------------------------------------"
echo "🎯 STACK IS READY"
echo "API: http://localhost:8000/docs"
echo "Grafana: http://localhost:3000 (admin/admin)"
echo "Airflow: http://localhost:8080 (admin/admin)"
echo "-------------------------------------------------------"
echo "Next: Run 'python heavy_load.py' to test the speed!"