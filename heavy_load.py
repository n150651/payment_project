import asyncio
import httpx
import time
import random

# --- CONFIGURATION ---
API_URL = "http://localhost:8000/transactions/"
API_KEY = "super-secret-payment-token-123"
HEADERS = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}
CONCURRENT_REQUESTS = 50  # Number of simultaneous "users"
TOTAL_REQUESTS = 2000

async def send_transaction(client):
    payload = {
        "user_id": random.randint(1, 1000),
        "amount": round(random.uniform(10.0, 15000.0), 2),
        "currency": "USD"
    }
    try:
        start_time = time.perf_counter()
        # Increased timeout to 30.0 to handle the burst
        response = await client.post(API_URL, json=payload, headers=HEADERS, timeout=30.0)
        end_time = time.perf_counter()
        
        if response.status_code == 200:
            return end_time - start_time
        else:
            return f"Error_{response.status_code}"
    except Exception as e:
        return f"Conn_Error_{type(e).__name__}"

async def run_stress_test():
    print(f"🚀 Starting Stress Test: {TOTAL_REQUESTS} transactions...")
    
    # We use a Semaphore to control exactly how many requests are active at once
    # This is the "Multi-threading" logic for the client side
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async def sem_task(client):
        async with semaphore:
            return await send_transaction(client)

    async with httpx.AsyncClient() as client:
        start_test = time.perf_counter()
        tasks = [sem_task(client) for _ in range(TOTAL_REQUESTS)]
        results = await asyncio.gather(*tasks)
        end_test = time.perf_counter()

    # Analysis
    latencies = [r for r in results if isinstance(r, float)]
    errors = [r for r in results if not isinstance(r, float)]
    
    total_time = end_test - start_test
    
    print("\n--- 📊 STRESS TEST RESULTS ---")
    print(f"Total Time:     {total_time:.2f} seconds")
    print(f"Successful TX:  {len(latencies)}")
    print(f"Failed TX:      {len(errors)}")
    
    if latencies:
        print(f"Avg Latency:    {sum(latencies)/len(latencies):.4f}s")
        print(f"Throughput:     {len(latencies) / total_time:.2f} TPS")
    
    if errors:
        # Show unique errors to see what went wrong
        print(f"Unique Errors:  {set(errors)}")

if __name__ == "__main__":
    asyncio.run(run_stress_test())