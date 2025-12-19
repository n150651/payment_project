import urllib.request
import json
import random
import time
import sys

URL = "http://localhost:8000/transactions/"

print("🟢 Real-Time Traffic Simulator Started... (Press Ctrl+C to stop)")

try:
    while True:
        # 1. Create Random Transaction
        payload = {
            "user_id": random.randint(100, 999),
            "amount": round(random.uniform(10.0, 1000.0), 2),
            "currency": "USD"
        }

        # 2. Send Request
        req = urllib.request.Request(
            URL, 
            data=json.dumps(payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                print(f"✅ Sent ${payload['amount']} - User {payload['user_id']}")
        except Exception as e:
            print(f"❌ Connection Failed: {e}")

        # 3. Random Sleep (Simulate human behavior)
        time.sleep(random.uniform(0.5, 2.0))

except KeyboardInterrupt:
    print("\n🛑 Traffic Stopped.")
    sys.exit(0)
