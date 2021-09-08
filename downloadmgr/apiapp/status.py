from flask import (
    Blueprint, render_template
)

from .db import get_db

bp = Blueprint("status", __name__, url_prefix="/")


@bp.route("/")
def home():
    db = get_db()
    segments = db.execute(
        'SELECT *'
        ' FROM segments s'
    ).fetchall()
    return render_template('index.html', segments=segments)


@bp.route("/id/<dl_id>")
def show_id_state(dl_id):
    db = get_db()
    query = ('SELECT *'
        ' FROM segments s'
        f' WHERE s.ytid = "{dl_id}"')
    segment = db.execute(query).fetchall()

    return render_template(
        'itemstate.html',
        dl_id=dl_id,
        segment=segment[0] if len(segment) else None
    )
