from flask import Blueprint, Flask, jsonify, request, g
from .db import get_db, RecordStatus

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/download/next", methods=["GET"])
def get_next_download():
    """Get the next item to download."""

    db = get_db()
    query = ('SELECT *'
        ' FROM segments s'
        " WHERE s.state IS NULL"
        ' ORDER BY RANDOM()'
        ' LIMIT 1'
    )
    segment = db.execute(query).fetchall()

    if len(segment) > 0:
        return jsonify({
            "download_id": segment[0]["ytid"],
            "success": True
        })
    else:
        return jsonify({
            "success": False,
            "message": "Query returned nothing."
        })


@bp.route("/download/<dl_id>", methods=["GET", "PUT"])
def update_download_state(dl_id: str):
    """Update the backend with the current download state, for this download ID."""
    db = get_db()

    if request.method == "GET":
        query = ('SELECT *'
            ' FROM segments s'
            f' WHERE s.ytid = "{dl_id}"')
        segment = db.execute(query).fetchall()

        if len(segment) > 0:
            return {
                "ytid": segment[0]["ytid"],
                "state": segment[0]["state"],
                "partition": segment[0]["partition"]
            }
        else:
            return jsonify({
                "success": False,
                "message": "Query returned nothing."
            })

    else:
        request_data = request.get_json()
        errorstate = False
        message = None

        update_str = ""
        for k, v in request_data.items():
            if k not in {"state"}:
                errorstate = True
                message = "Bad update key"
            elif v not in RecordStatus.values():
                errorstate = True
                message = "Bad update value"
            else:
                update_str += f"{k} = '{v}'"
            
            if errorstate:
                break

        if not errorstate and len(update_str) > 0:
            query = (
                'UPDATE segments SET ' + update_str +
                f' WHERE ytid = "{dl_id}"'
            )
            cursor = db.execute(query)
            db.commit()

            return jsonify({
                "success": True
            })
        else:
            return jsonify({
                "success": False,
                "message": message
            })


@bp.route("/download/batch", methods=["POST"])
def batch_update_item_state():
    return jsonify({
        "success": False
    })
