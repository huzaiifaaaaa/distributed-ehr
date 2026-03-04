#!/usr/bin/env python3
"""
Performance test for EHR API
- Sends multiple concurrent requests
- Measures response times
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:5001"  # API URL

# define endpoints to test
TEST_ENDPOINTS = [
    {"method": "GET", "path": "/patients"},
    {"method": "GET", "path": "/users"},
    {"method": "POST", "path": "/patients", "json": {
        "full_name": "Performance Test",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "phone": "555-0000",
        "address": "123 Test St"
    }},
]

NUM_REQUESTS = 500  # Number of requests to send
NUM_THREADS = 10   # Number of concurrent threads

def send_request(endpoint):
    method = endpoint["method"]
    url = BASE_URL + endpoint["path"]
    json_data = endpoint.get("json")
    
    start = time.time()
    try:
        if method == "GET":
            r = requests.get(url)
        elif method == "POST":
            r = requests.post(url, json=json_data)
        elif method == "PUT":
            r = requests.put(url, json=json_data)
        elif method == "DELETE":
            r = requests.delete(url)
        else:
            return None
        elapsed = time.time() - start
        return {"status": r.status_code, "time": elapsed, "url": url}
    except Exception as e:
        elapsed = time.time() - start
        return {"status": "ERROR", "time": elapsed, "url": url, "error": str(e)}

def run_performance_test():
    results = []
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(send_request, TEST_ENDPOINTS[i % len(TEST_ENDPOINTS)])
                   for i in range(NUM_REQUESTS)]
        for future in as_completed(futures):
            results.append(future.result())
    
    # Print stats
    total_time = sum(r["time"] for r in results if r["status"] != "ERROR")
    avg_time = total_time / len([r for r in results if r["status"] != "ERROR"])
    success_count = len([r for r in results if r["status"] in (200, 201)])
    error_count = len([r for r in results if r["status"] == "ERROR"])

    print(f"\n--- Performance Test Summary ---")
    print(f"Total requests: {NUM_REQUESTS}")
    print(f"Successful responses: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Average response time: {avg_time:.3f} sec")
    print(f"Max response time: {max(r['time'] for r in results):.3f} sec")
    print(f"Min response time: {min(r['time'] for r in results):.3f} sec")

if __name__ == "__main__":
    run_performance_test()