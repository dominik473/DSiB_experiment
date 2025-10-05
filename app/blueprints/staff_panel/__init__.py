from flask import Blueprint, abort
from flask_login import current_user

# nazwa blueprintu = "staff" → endpointy typu 'staff.dashboard'
bp = Blueprint("staff", __name__, url_prefix="/staff")

@bp.before_request
def _gate():
    if not getattr(current_user, "is_authenticated", False):
        return None  # Flask-Login przekieruje do login_view
    if current_user.role not in {"staff", "admin"}:
        abort(403)

# ⬇️ KLUCZOWE: załaduj moduł z trasami, aby dodefiniował endpointy na bp
from . import routes  # noqa: E402,F401
