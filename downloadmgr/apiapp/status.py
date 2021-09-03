from flask import (
    Blueprint, render_template
)

bp = Blueprint("status", __name__, url_prefix="/")


@bp.route("/")
def home():
    return "<p>Hello, World!</p>"


@bp.route("/id/<dl_id>")
def show_id_state(dl_id):
    return f"<p>Show state for: {dl_id}"
