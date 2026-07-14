# Assignment: System Design
**Student Name:** [Raj Patil]  
**Date:** July 2026  
**GitHub Repository:** https://github.com/RAJ-A58/SystemDesign  

---

## 1. Project Overview
This document details the step-by-step implementation of three interconnected system design mini-projects built with Python and Flask:
1. **Task 1 – URL Shortener Lite:** A lightweight service using Base62 encoding and in-memory/database storage for URL redirection.
2. **Task 2 – Rate Limiter Mini:** A sliding window log API protection layer restricting users to 5 requests per minute.
3. **Task 3 – Load Balancer Simulation:** A round-robin traffic distributor routing incoming requests across multiple backend servers.

---

## 2. Step-by-Step Implementation

### Task 2: Rate Limiter Mini

#### A. Process Description & Architectural Decisions
- **Algorithm Choice:** We implemented the **Sliding Window Log** algorithm instead of a Fixed Window Counter. Fixed Window Counters suffer from boundary burst flaws (e.g., sending 5 requests at 12:00:59 and 5 requests at 12:01:01 allows 10 requests in 2 seconds). The Sliding Window Log records exact request timestamps and prunes timestamps older than 60 seconds (`current_time - 60`), guaranteeing 100% precision.
- **Data Structure:** We used a Python In-Memory Dictionary (`dict[str, list[float]]`) where each key is a `user_id` string and each value is a list of float timestamps (`[1720516800.1, 1720516805.4]`).
- **HTTP Status Codes:** When a user exceeds 5 requests within the active 60-second window, the API returns industry-standard **HTTP 429 Too Many Requests** along with JSON error formatting.

#### B. Code Snippets & Explanations

**1. Core Algorithm (`rate_limiter/rate_limiter.py`):**
```python
import time

class RateLimiter:
    def __init__(self, max_request=5, window_seconds=60):
        self.limit = max_request
        self.window_seconds = window_seconds
        self.users = {}  # { "user_id": [timestamp1, timestamp2, ...] }

    def is_allowed(self, user_id):
        curr_time = time.time()
        if user_id not in self.users:
            self.users[user_id] = []

        # Prune timestamps older than 60 seconds
        window_start = curr_time - self.window_seconds
        valid_timestamps = []
        for t in self.users[user_id]:
            if t > window_start:
                valid_timestamps.append(t)
        self.users[user_id] = valid_timestamps

        # Check if remaining requests are under the limit
        if len(self.users[user_id]) < self.limit:
            self.users[user_id].append(curr_time)
            return True
        else:
            return False
```

**2. Flask API Endpoint (`rate_limiter/api.py`):**
```python
from flask import Flask, request, jsonify
from rate_limiter import RateLimiter

app = Flask(__name__)
limiter = RateLimiter(max_request=5, window_seconds=60)

@app.route("/data", methods=["GET"])
def get_data():
    user_id = request.args.get("user_id", "default_user")

    if limiter.is_allowed(user_id):
        return jsonify({"status": "success", "message": "Data retrieved."}), 200
    else:
        return jsonify({
            "error": "Too Many Requests: Try again later.",
            "message": "Too Many Requests: Try again later."
        }), 429

if __name__ == "__main__":
    app.run(port=5000, debug=True)
```

#### C. Verification & Screenshots Checklist
- [ ] **Screenshot 1: Terminal running `python api.py`** showing the server listening on `http://127.0.0.1:5000`.
- [ ] **Screenshot 2: Browser/Postman Successful Requests (1 to 5)** accessing `http://127.0.0.1:5000/data?user_id=alice` returning `HTTP 200 OK`.
- [ ] **Screenshot 3: Browser/Postman Rate-Limited Request (6th Request)** showing `HTTP 429 Too Many Requests` and `"Too Many Requests: Try again later."`.

---

### Task 1: URL Shortener Lite

#### A. Process Description & Architectural Decisions
- **Algorithm Choice:** We implemented a **Base62 Encoding Algorithm** (`0-9`, `a-z`, `A-Z` = 62 alphanumeric characters) to generate short, URL-safe identifiers (e.g., `g8`). Every time a URL is submitted, an internal auto-incrementing counter (`self.counter`) is converted from decimal integer format into Base62 string format (`num % 62` remainder lookups).
- **Data Storage:** We used a Python In-Memory Dictionary (`dict[str, str]`) mapping `short_id` keys directly to `long_url` values (`{"g8": "https://github.com/RAJ-A58/SystemDesign"}`).
- **HTTP Methods & Status Codes:**
  - `POST /shorten`: Adheres to RESTful standards for resource creation (`HTTP 201 Created`).
  - `GET /<short_id>`: Uses **HTTP 302 Found (Redirect)** to immediately forward the client browser to the original destination URL.

#### B. Code Snippets & Explanations

**1. Base62 Encoder Class (`url_shortener/shortener.py`):**
```python
import string

class URLShortener:
    def __init__(self):
        # 62 characters for Base62: '0-9', 'a-z', 'A-Z'
        self.characters = string.digits + string.ascii_letters
        self.base = len(self.characters)  # 62
        self.url_map = {}
        self.counter = 1000  # Start at 1000 so IDs are at least 2 characters long

    def encode(self, num):
        """Encodes an integer into a Base62 string."""
        if num == 0:
            return self.characters[0]
        encoded = []
        while num > 0:
            remainder = num % self.base
            encoded.append(self.characters[remainder])
            num //= self.base
        return ''.join(reversed(encoded))

    def shorten(self, long_url):
        """Creates unique Base62 short ID and saves URL mapping."""
        short_id = self.encode(self.counter)
        self.url_map[short_id] = long_url
        self.counter += 1
        return short_id

    def get_url(self, short_id):
        """Retrieves original long URL for redirection."""
        return self.url_map.get(short_id)
```

**2. Flask API Wrapper (`url_shortener/api.py`):**
```python
from flask import Flask, request, jsonify, redirect
from shortener import URLShortener

app = Flask(__name__)
shortener = URLShortener()

@app.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Please provide a valid 'url' inside JSON."}), 400

    long_url = data["url"]
    short_id = shortener.shorten(long_url)
    short_link = f"http://127.0.0.1:5001/{short_id}"

    return jsonify({
        "message": "URL shortened successfully!",
        "short_id": short_id,
        "short_url": short_link,
        "original_url": long_url
    }), 201

@app.route("/<short_id>", methods=["GET"])
def redirect_to_url(short_id):
    original_url = shortener.get_url(short_id)
    if original_url:
        return redirect(original_url)  # HTTP 302 Redirect
    else:
        return jsonify({"error": f"Short URL ID '{short_id}' not found!"}), 404

if __name__ == "__main__":
    app.run(port=5001, debug=True)
```

#### C. Verification & Screenshots Checklist
- [x] **Screenshot 1: Postman `POST /shorten` Request** showing `HTTP 201 CREATED` with JSON payload returning `"short_id": "g9"`.
- [ ] **Screenshot 2: Browser Redirect (`GET /g9`)** showing the browser navigating to the destination GitHub repository.

---

### Task 3: Load Balancer Simulation

#### A. Process Description & Architectural Decisions
- **Algorithm Choice:** We implemented the **Round-Robin Load Balancing Algorithm**. Round-Robin uniformly distributes incoming network traffic across a cluster of backend servers sequentially (`Server 1` $\rightarrow$ `Server 2` $\rightarrow$ `Server 3` $\rightarrow$ `Server 1`). We track the active target using a thread-safe index variable (`(current_index + 1) % len(BACKEND_SERVERS)` inside `threading.Lock`).
- **Multiprocessing Server Architecture:** To cleanly simulate multiple independent physical machines from a single local workstation, we used Python's `multiprocessing.Process` module to launch 3 independent Flask servers running on distinct ports (`5002`, `5003`, and `5004`).
- **Proxy Forwarding:** The central load balancer (`port 8000`) acts as a reverse proxy using Python's `requests` library to relay client headers, payloads, and HTTP methods directly to the selected target backend, returning the backend's exact response (`Hello from Server X!`) back to the client.

#### B. Code Snippets & Explanations

**1. Mock Backend Servers Launcher (`load_balancer/servers.py`):**
```python
from multiprocessing import Process
from flask import Flask

def create_server(server_name, port):
    """Creates mock backend server returning unique identifier string."""
    app = Flask(server_name)

    @app.route("/", methods=["GET"])
    def home():
        return f"Hello from {server_name}! (Running on port {port})\n"

    print(f"[{server_name}] Starting on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    servers = [("Server 1", 5002), ("Server 2", 5003), ("Server 3", 5004)]
    processes = [Process(target=create_server, args=(name, port)) for name, port in servers]
    for p in processes: p.start()
    for p in processes: p.join()
```

**2. Round-Robin Load Balancer Proxy (`load_balancer/lb.py`):**
```python
from flask import Flask, request, jsonify
import requests
from threading import Lock

app = Flask(__name__)
BACKEND_SERVERS = ["http://127.0.0.1:5002", "http://127.0.0.1:5003", "http://127.0.0.1:5004"]
current_index = 0
lock = Lock()

def get_next_server():
    """Selects next server via Round-Robin modulo rotation."""
    global current_index
    with lock:
        server = BACKEND_SERVERS[current_index]
        current_index = (current_index + 1) % len(BACKEND_SERVERS)
        return server

@app.route("/", methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_request(path=""):
    target_server = get_next_server()
    target_url = f"{target_server}/{path}"
    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={k: v for k, v in request.headers if k != 'Host'},
            data=request.get_data(),
            timeout=5
        )
        return resp.content, resp.status_code, dict(resp.headers)
    except requests.exceptions.RequestException:
        return jsonify({"error": "502 Bad Gateway", "message": f"Server {target_server} down."}), 502

if __name__ == "__main__":
    app.run(port=8000, debug=True)
```

#### C. Verification & Screenshots Checklist
- [ ] **Screenshot 1: Terminal running `python servers.py`** showing all 3 mock servers (`Server 1`, `Server 2`, `Server 3`) active on ports `5002`, `5003`, and `5004`.
- [ ] **Screenshot 2: Terminal running `python lb.py`** showing the Load Balancer active on port `8000`.
- [ ] **Screenshot 3: Sequential Requests (`GET http://127.0.0.1:8000/`)** showing Round-Robin rotation cycling across `Hello from Server 1!`, `Hello from Server 2!`, and `Hello from Server 3!`.

---

## 3. Final Notes & Key Learnings
- **Challenges Faced:** Understanding the difference between fixed windows vs. sliding window logs, and correctly configuring Flask routing paths (`/data`).
- **Key Learnings:** How sliding window logs prevent API burst abuse, and how HTTP 429 serves as the standard contract between APIs and clients for rate limiting.
