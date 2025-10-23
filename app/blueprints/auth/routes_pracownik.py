from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from . import bp
from app.forms.auth import LoginForm
from app.extensions import login_manager
from app.models.pracownik import Pracownik


@login_manager.user_loader
def load_user(user_id: str):
    try:
        return Pracownik.query.get(int(user_id))
    except Exception:
        return None


def _role_redirect(u: Pracownik):
    role = (u.role or "").lower()
    if role == "client":
        return redirect(url_for("client.home"))
    return redirect(url_for("staff.dashboard"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _role_redirect(current_user)

    form = LoginForm()
    if form.validate_on_submit():
        user = Pracownik.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_url = request.args.get("next")
            return redirect(next_url) if next_url else _role_redirect(user)
        flash("Błędny email lub hasło", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))