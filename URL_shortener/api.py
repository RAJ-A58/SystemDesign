from flask import Flask, request, jsonify, redirect
from shortener import URLShortener

# Create our web application server
app = Flask(__name__)

# Create our URL shortener helper (which stores mappings like {'g8': 'https://google.com'})
shortener = URLShortener()


@app.route("/shorten", methods=["POST"])
def shorten_url():
    """
    This function runs when someone sends a POST request with JSON data to /shorten.
    Example payload: {"url": "https://google.com"}
    """
    # 1. Read the JSON dictionary sent by the user
    data = request.get_json()

    # 2. Check if the user forgot to include the "url" key inside the JSON
    if not data or "url" not in data:
        return jsonify({"error": "Please provide a valid 'url' inside your JSON request."}), 400  # 400 means "Bad Request"

    # 3. Extract the long URL string from the dictionary
    long_url = data["url"]

    # 4. Ask our URLShortener to generate a short ID (like 'g8') and save it in memory
    short_id = shortener.shorten(long_url)

    # 5. Build the complete clickable short link
    short_link = f"http://127.0.0.1:5001/{short_id}"

    # 6. Send back a JSON response telling the user their new short link
    return jsonify({
        "message": "URL shortened successfully!",
        "short_id": short_id,
        "short_url": short_link,
        "original_url": long_url
    }), 201  # 201 means "New resource created successfully"


@app.route("/<short_id>", methods=["GET"])
def redirect_to_url(short_id):
    """
    This function runs when someone visits a short link in their browser.
    Example URL: http://127.0.0.1:5001/g8
    """
    # 1. Look up the short_id ('g8') inside our URLShortener dictionary
    original_url = shortener.get_url(short_id)

    # 2. If we found the original URL, redirect the browser to that page immediately
    if original_url:
        return redirect(original_url)  # HTTP 302 Redirect

    # 3. If the short_id does not exist, return a 404 Not Found error
    else:
        return jsonify({"error": f"Short URL ID '{short_id}' does not exist!"}), 404  # 404 means "Not Found"


if __name__ == "__main__":
    # We run on port 5001 so it doesn't clash with our Rate Limiter on port 5000
    print("Starting URL Shortener API on http://127.0.0.1:5001")
    app.run(port=5001, debug=True)
