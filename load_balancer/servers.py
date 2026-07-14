from multiprocessing import Process
from flask import Flask

def create_server(server_name, port):
    """
    Creates and runs a mock Flask backend server on a specific port.
    Returns: 'Hello from Server X!'
    """
    app = Flask(server_name)

    @app.route("/", methods=["GET"])
    def home():
        return f"Hello from {server_name}! (Running on port {port})\n"

    print(f"[{server_name}] Starting on http://127.0.0.1:{port}")
    # Disable reloader and debug when running in background processes
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # List of our 3 mock backend servers and their target ports
    servers = [
        ("Server 1", 5002),
        ("Server 2", 5003),
        ("Server 3", 5004)
    ]

    processes = []
    print("=" * 60)
    print("STARTING 3 MOCK BACKEND SERVERS SIMULTANEOUSLY...")
    print("=" * 60)

    # Launch each server in a separate multiprocessing process
    for name, port in servers:
        p = Process(target=create_server, args=(name, port))
        p.start()
        processes.append(p)

    try:
        # Keep the main process alive while child servers run
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nStopping all backend servers...")
        for p in processes:
            p.terminate()
