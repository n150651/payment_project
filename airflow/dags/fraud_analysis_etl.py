from airflow import DAG
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import csv
import os

# --- SETTINGS ---
FRAUD_THRESHOLD = 10000  # Any transaction above this is "Suspicious"
REPORT_PATH = "/opt/airflow/logs/fraud_reports"  # Where to save the output

def analyze_fraud_transactions(**context):
    # 1. EXTRACT (Read from Replica)
    mysql_hook = MySqlHook(mysql_conn_id='payment_db_replica')
    # Fetch user_id, amount, currency
    sql = "SELECT id, user_id, amount, currency FROM transactions;"
    transactions = mysql_hook.get_records(sql)
    
    print(f"📥 Extracted {len(transactions)} transactions from Replica.")

    # 2. TRANSFORM (Find High-Value transactions)
    suspicious_txns = []
    total_fraud_amount = 0

    for txn in transactions:
        txn_id, user_id, amount, currency = txn
        
        # Convert decimal/float if needed and check threshold
        if float(amount) > FRAUD_THRESHOLD:
            print(f"⚠️  ALERT: Fraud detected! ID: {txn_id}, Amount: {amount}")
            suspicious_txns.append(txn)
            total_fraud_amount += float(amount)

    # 3. LOAD (Save Report to Disk)
    # Ensure directory exists
    os.makedirs(REPORT_PATH, exist_ok=True)
    
    # Generate a filename with today's date
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{REPORT_PATH}/fraud_report_{date_str}.csv"

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Transaction ID", "User ID", "Amount", "Currency", "Status"])
        
        for s_txn in suspicious_txns:
            writer.writerow([s_txn[0], s_txn[1], s_txn[2], s_txn[3], "FLAGGED_FRAUD"])
            
    print(f"✅ Analysis Complete.")
    print(f"📊 Total Suspicious Transactions: {len(suspicious_txns)}")
    print(f"💰 Total Fraud Volume: {total_fraud_amount}")
    print(f"📂 Report saved to: {filename}")

# --- DAG DEFINITION ---
default_args = {
    'owner': 'data_team',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='02_fraud_analysis_etl',
    default_args=default_args,
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',  # Runs once a day automatically
    catchup=False
) as dag:

    run_analysis = PythonOperator(
        task_id='detect_suspicious_activity',
        python_callable=analyze_fraud_transactions
    )

    run_analysis
