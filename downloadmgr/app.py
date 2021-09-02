from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    return "<p>Hello, World!</p>"


@app.route("/id/<dl_id>")
def show_id_state(dl_id):
    return f"<p>Show state for: {dl_id}"


@app.route("/api/download/next", methods=["GET"])
def get_next_download():
    """Get the next item to download."""
    return jsonify({
        "download_id": "foobar",
        "segment": None
    })


@app.route("/api/download/<dl_id>", methods=["GET", "PUT"])
def update_download_state(dl_id: str):
    """Update the backend with the current download state, for this download ID."""
    if request.method == "GET":
        return {
            "id": dl_id
        }
    else:
        return jsonify({
            "success": True
        })


@app.route("/api/download/batch", methods=["POST"])
def batch_update_item_state():
    return jsonify({
        "success": False
    })
