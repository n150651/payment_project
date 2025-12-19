from airflow import DAG
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# 1. Define the Python Function to run
def check_replica_connection():
    # Connect using the Connection ID we defined in docker-compose (AIRFLOW_CONN_PAYMENT_DB_REPLICA)
    # This automatically finds the user/pass from your .env file!
    mysql_hook = MySqlHook(mysql_conn_id='payment_db_replica')
    
    # Run a simple query
    records = mysql_hook.get_records("SELECT COUNT(*) FROM transactions;")
    
    print(f"✅ SUCCESSFULLY CONNECTED TO REPLICA!")
    print(f"📊 Total Transactions found: {records[0][0]}")

# 2. Define the DAG settings
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='01_check_db_connection',
    default_args=default_args,
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,  # Run manually for now
    catchup=False
) as dag:

    # 3. Create the Task
    check_db_task = PythonOperator(
        task_id='check_replica_connectivity',
        python_callable=check_replica_connection
    )

    check_db_task
