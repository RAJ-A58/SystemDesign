from flask import Flask, request, jsonify
import requests
from threading import Lock

# Create the Load Balancer web application
app = Flask(__name__)

# Our 3 backend server URLs running from servers.py
BACKEND_SERVERS = [
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003",
    "http://127.0.0.1:5004"
]

# Track current server index for Round-Robin rotation
current_index = 0
lock = Lock()  # Ensure thread safety when modifying current_index

def get_next_server():
    """
    Round-Robin Algorithm:
    Selects the next backend server in order and rotates back to index 0 after the last server.
    """
    global current_index
    with lock:
        server = BACKEND_SERVERS[current_index]
        # Cycle: 0 -> 1 -> 2 -> 0 -> 1 -> 2...
        current_index = (current_index + 1) % len(BACKEND_SERVERS)
        return server

@app.route("/", methods=["GET"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_request(path=""):
    """
    Intercepts incoming requests, picks the next backend server via Round-Robin,
    and forwards the request using the requests library.
    """
    target_server = get_next_server()
    target_url = f"{target_server}/{path}"

    try:
        # Forward request to the chosen backend server
        print(f"[Round-Robin LB] Forwarding request to -> {target_url}")
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            timeout=5
        )
        return resp.content, resp.status_code, dict(resp.headers)

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Backend server {target_server} is unreachable or down.")
        return jsonify({
            "error": "502 Bad Gateway",
            "message": f"Backend server {target_server} failed to respond."
        }), 502

@app.route("/status", methods=["GET"])
def lb_status():
    """Helper endpoint to inspect load balancer target list and current index."""
    return jsonify({
        "load_balancer": "Round-Robin Simulation",
        "backend_servers": BACKEND_SERVERS,
        "next_target_index": current_index,
        "next_target_url": BACKEND_SERVERS[current_index]
    })

if __name__ == "__main__":
    print("=" * 60)
    print("STARTING ROUND-ROBIN LOAD BALANCER ON http://127.0.0.1:8000")
    print("=" * 60)
    app.run(port=8000, debug=True)
