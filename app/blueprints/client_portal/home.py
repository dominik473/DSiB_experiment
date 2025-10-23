from flask import render_template
from flask_login import login_required
from . import bp


@bp.route("/", endpoint="home")
@login_required
def home():
    try:
        return render_template("client_portal/dashboard.html")
    except Exception:
        return "Client Home", 200