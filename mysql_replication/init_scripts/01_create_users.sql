-- 1. Create the Replication User (used by the Replica server)
CREATE USER 'repl_user'@'%' IDENTIFIED BY 'ReplicaPass123!';
GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'%';

-- 2. Create the Application User (used by Python/FastAPI)
CREATE USER 'app_user'@'%' IDENTIFIED BY 'AppPass123!';
GRANT ALL PRIVILEGES ON *.* TO 'app_user'@'%';

FLUSH PRIVILEGES;
