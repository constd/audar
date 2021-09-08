from flask import Blueprint, Flask, jsonify, request, g
from .db import get_db, RecordStatus

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/segments/<ytid>", methods=["GET"])
def get_segment_info(ytid):
    db = get_db()

    query = ('SELECT *'
        ' FROM segments s'
        f' WHERE s.ytid = "{ytid}"')
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


@bp.route("/segments/count", methods=["GET"])
def get_segments_count():
    """
    Get segment counts. You may use query paramters to select
    different subsets.

    Examples using httpie:
    ```
    http "localhost:5000/api/segments/count?state=completed"
    http "localhost:5000/api/segments/count?partition=unbalanced_train"
    ```
    """
    db = get_db()

    # by state
    if "state" in request.args:
        if request.args["state"] is None or request.args["state"] in ["null", "NULL", "none", "None"]:
            seg_filter = "WHERE state IS NULL"
        else:
            seg_filter = f"WHERE state = '{request.args['state']}'"
    # by partition
    elif "partition" in request.args:
        if request.args["partition"] is None  or request.args["partition"] in ["null", "NULL", "none", "None"]:
            seg_filter = "WHERE partition IS NULL"
        else:
            seg_filter = f"WHERE partition = '{request.args['partition']}'"
    else:
        seg_filter = ""

    query = "SELECT COUNT(*) from segments " + seg_filter

    cursor = db.execute(query)
    count_result = None
    for row in cursor:
        for member in row:
            if member is not None:
                count_result = member

    return jsonify({
        "count": count_result
    })


@bp.route("/download/next", methods=["GET"])
def get_next_download():
    """Get the next item to download.
    
    An example using httpie:
    ```
    http PUT localhost:5000/api/download/next
    ```
    """

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


@bp.route("/download/<ytid>", methods=["PUT"])
def update_download_state(ytid: str):
    """Update the backend with the current download state, for this download ID.
    
    An example using httpie:
    ```
    http PUT localhost:5000/api/download/ohWowNrFc8U state=completed
    ```
    """
    db = get_db()

    if request.method == "PUT":
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
                f' WHERE ytid = "{ytid}"'
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
    """Update the state of many ytid's using a POST request.
    
    An example using httpie:
    ```
    http -v POST "localhost:5000/api/download/batch" \
        state=completed \
        ytids:='["--0B3G_C3qc", "--0PQM4-hqg", "---EDNidJUA"]'
    ```
    """
    request_data = request.get_json()

    success = True
    message = None

    if request_data is None:
        success = False
        message = "Post body must not be empty."
    elif "state" not in request_data:
        success = False
        message = "post body must include 'state'"
    elif "ytids" not in request_data or not isinstance(request_data["ytids"], list):
        success = False
        message = "post body must include a list with key 'ytids'"
    elif request_data["state"] not in RecordStatus.values():
        success = False
        message = f"state value is not valid; must be in ({RecordStatus.values()})"
    
    if success:
        db = get_db()
        new_state = request_data["state"]

        for ytid in request_data["ytids"]:
            query = (
                    f'UPDATE segments SET state = "{new_state}"'
                    f' WHERE ytid = "{ytid}"'
                )
            db.execute(query)
        db.commit()

        return jsonify({
            "success": True
        })

    else:
        return jsonify({
                "success": False,
                "message": message
            })
