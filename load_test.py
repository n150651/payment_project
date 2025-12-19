import urllib.request
import json
import random
import time

# Target URL
url = "http://localhost:8000/transactions/"

print("🚀 Starting Load Test: Sending 100 Transactions...")

for i in range(100):
    # 1. Randomize Data
    # 10% chance of being a FRAUD transaction (> $10,000)
    if random.random() < 0.1:
        amount = round(random.uniform(10001.0, 50000.0), 2)
        print(f"⚠️  Generated FRAUD attempt: ${amount}")
    else:
        amount = round(random.uniform(10.0, 5000.0), 2)

    payload = {
        "user_id": random.randint(100, 999),
        "amount": amount,
        "currency": "USD"
    }
    
    # 2. Send Request
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"[{i+1}/100] ✅ Sent ${amount} (User {payload['user_id']})")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Wait slightly to simulate realistic traffic (2 requests/sec)
    time.sleep(0.5)

print("🏁 Load Test Complete!")
