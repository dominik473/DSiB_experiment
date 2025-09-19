from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.forms.auth import LoginForm
from app.models.user import User
from . import bp

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("staff.dashboard"))  # domyślnie
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_url = request.args.get("next") or url_for("staff.dashboard")
            return redirect(next_url)
        flash("Błędny email lub hasło", "danger")
    return render_template("auth/login.html", form=form)

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("public.index"))
