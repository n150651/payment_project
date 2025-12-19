import urllib.request
import json
import random
import concurrent.futures
import time

URL = "http://localhost:8000/transactions/"
TOTAL_REQUESTS = 10000
CONCURRENT_USERS = 10

def send_transaction(index):
    # 1. Randomize Data (15% Fraud Chance)
    if random.random() < 0.15:
        amount = round(random.uniform(10001.0, 50000.0), 2)
    else:
        amount = round(random.uniform(10.0, 5000.0), 2)

    payload = {
        "user_id": random.randint(100, 999),
        "amount": amount,
        "currency": "USD"
    }

    req = urllib.request.Request(
        URL, 
        data=json.dumps(payload).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return f"✅ #{index} Sent ${amount}"
    except Exception as e:
        return f"❌ #{index} Failed: {e}"

print(f"🔥 STARTING HEAVY LOAD: {TOTAL_REQUESTS} Transactions with {CONCURRENT_USERS} threads...")
start_time = time.time()

# 2. Run in Parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
    results = list(executor.map(send_transaction, range(TOTAL_REQUESTS)))

duration = time.time() - start_time
print(f"🏁 FINISHED in {duration:.2f} seconds!")
print(f"⚡ Throughput: {TOTAL_REQUESTS / duration:.2f} Transactions per Second (TPS)")
