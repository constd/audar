from flask import Blueprint, Flask, jsonify, request, g
# import db

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/download/next", methods=["GET"])
def get_next_download():
    """Get the next item to download."""
    return jsonify({
        "download_id": "foobar",
        "segment": None
    })


@bp.route("/download/<dl_id>", methods=["GET", "PUT"])
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


@bp.route("/download/batch", methods=["POST"])
def batch_update_item_state():
    return jsonify({
        "success": False
    })
