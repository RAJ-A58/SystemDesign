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

**1. Core Algorithm (`task2_Rate_limiter/rate_limiter.py`):**
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

**2. Flask API Endpoint (`task2_Rate_limiter/api.py`):**
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
*(In Progress...)*

---

### Task 3: Load Balancer Simulation
*(In Progress...)*

---

## 3. Final Notes & Key Learnings
- **Challenges Faced:** Understanding the difference between fixed windows vs. sliding window logs, and correctly configuring Flask routing paths (`/data`).
- **Key Learnings:** How sliding window logs prevent API burst abuse, and how HTTP 429 serves as the standard contract between APIs and clients for rate limiting.
