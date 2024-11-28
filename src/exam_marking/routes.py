import sqlite3
from itertools import zip_longest

from flask import Blueprint, g, render_template, request

bp = Blueprint("routes", __name__)


@bp.route("/")
def index():
    first_unmarked = None
    for row in g.marks:
        if all(m is None for m in row["marks"]):
            first_unmarked = row["zid"]
            break
    return render_template(
        "index.html",
        zip_longest=zip_longest,
        enumerate=enumerate,
        first_unmarked=first_unmarked,
    )


save_period = 10


@bp.route("/change", methods=["POST"])
def change():
    # Yeah this isn't pretty, but whatever.
    global save_period

    zid = request.form.get("zid")
    marks = []
    for i, col in enumerate(g.columns):
        marks.append(request.form.get(f"marks-{i}"))

    for row in g.marks:
        if row["zid"] == zid:
            row["marks"] = [m if m is not None else 0 for m in marks]

    if save_period == 0:
        g.save()
        save_period = 10
    else:
        save_period -= 1

    return "", 204
