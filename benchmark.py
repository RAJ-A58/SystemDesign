import time
import requests
import concurrent.futures

# Configuration
CONCURRENCY = 50       # Number of concurrent client requests
TOTAL_REQUESTS = 200   # Total requests to send in the test
SINGLE_SERVER_URL = "http://127.0.0.1:5002/"
LOAD_BALANCER_URL = "http://127.0.0.1:8000/"

def fetch(url):
    """Sends a single GET request and returns (latency, success_boolean)"""
    start = time.time()
    try:
        r = requests.get(url, timeout=5)
        success = (r.status_code == 200)
    except Exception:
        success = False
    return time.time() - start, success

def run_load_test(name, url, concurrency, total_requests):
    print(f"--- Testing {name} ---")
    print(f"URL: {url} | Concurrency: {concurrency} | Total Requests: {total_requests}")
    
    start_time = time.time()
    latencies = []
    success_count = 0
    
    # Fire requests concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(fetch, url) for _ in range(total_requests)]
        for f in concurrent.futures.as_completed(futures):
            lat, ok = f.result()
            latencies.append(lat)
            if ok:
                success_count += 1
                
    total_time = time.time() - start_time
    avg_latency = (sum(latencies) / len(latencies)) if latencies else 0
    
    print(f"Success Rate:    {success_count/total_requests * 100:.1f}% ({success_count}/{total_requests})")
    print(f"Average Latency: {avg_latency*1000:.2f} ms")
    print(f"Total Time:      {total_time:.2f} seconds")
    print(f"Throughput:      {total_requests/total_time:.2f} req/sec\n")
    return avg_latency

if __name__ == "__main__":
    print("Make sure servers.py and lb.py are running before starting the benchmark!\n")
    
    # 1. Test a single server directly
    avg_lat_single = run_load_test("Single Backend Server", SINGLE_SERVER_URL, CONCURRENCY, TOTAL_REQUESTS)
    
    # 2. Test the Load Balancer
    avg_lat_lb = run_load_test("Round-Robin Load Balancer", LOAD_BALANCER_URL, CONCURRENCY, TOTAL_REQUESTS)
    
    # 3. Calculate latency improvement
    if avg_lat_single > 0 and avg_lat_lb > 0:
        if avg_lat_lb < avg_lat_single:
            improvement = ((avg_lat_single - avg_lat_lb) / avg_lat_single) * 100
            print(f"RESULT: Load Balancer decreased average response latency by {improvement:.2f}%!")
        else:
            print("RESULT: Load Balancer was slower. (Note: To see improvement in a local test, add 'time.sleep(0.1)' to servers.py to simulate heavy processing so parallelization overtakes proxy overhead).")
