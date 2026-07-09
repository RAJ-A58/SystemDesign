from flask import Flask, request, jsonify

from rate_limiter import RateLimiter

app=Flask(__name__)
# Create a RateLimiter instance with default settings (5 requests per 60 seconds)

limiter = RateLimiter(max_request=5, window_seconds=60)
@app.route("/data", methods=["GET"])
def get_data():
  user_id = request.args.get("user_id", "default_user")

  if limiter.is_allowed(user_id):
    return jsonify({"status": "success", "message": "Data retrieved."}), 200
  else:
    return (
        jsonify({
            "error": "Too Many Requests: Try again later.",
            "message": "Too Many Requests: Try again later.",
        }),
        429,
    )
    
if __name__ == "__main__":
  app.run(port=5000, debug=True)