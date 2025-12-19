from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from datetime import datetime, timedelta
import pandas as pd
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def analyze_fraud_in_batches():
    # Connect to the REPLICA to avoid slowing down the Master/Source
    hook = MySqlHook(mysql_conn_id='payment_db_replica')
    
    # DBA Strategy: Process in chunks to keep memory usage low
    chunk_size = 5000
    fraud_threshold = 10000.00
    report_path = f"/opt/airflow/logs/fraud_reports/report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    
    query = f"SELECT * FROM transactions WHERE amount > {fraud_threshold} AND status = 'SUCCESS'"
    
    # Use Pandas with a chunked iterator for memory efficiency
    engine = hook.get_sqlalchemy_engine()
    
    print("Starting Fraud Analysis...")
    
    first_chunk = True
    for chunk in pd.read_sql(query, engine, chunksize=chunk_size):
        # Add logic: Mark as FLAGGED
        chunk['fraud_status'] = 'FLAGGED_FRAUD'
        
        # Write to CSV (Append mode)
        mode = 'w' if first_chunk else 'a'
        header = True if first_chunk else False
        chunk.to_csv(report_path, mode=mode, index=False, header=header)
        
        first_chunk = False
        print(f"Processed a batch of {len(chunk)} potential fraud cases.")

with DAG(
    '02_fraud_analysis_etl_v2',
    default_args=default_args,
    description='High-performance batch fraud analysis',
    schedule_interval='@hourly',  # Run every hour for "near real-time" feel
    catchup=False
) as dag:

    run_analysis = PythonOperator(
        task_id='analyze_fraud',
        python_callable=analyze_fraud_in_batches,
    )