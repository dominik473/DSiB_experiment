from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    surname = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="client")  # client/staff/admin

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def validate_staff_identity(user: "User") -> None:
    """
    Wymuś uzupełnienie name+surname dla staff/admin na poziomie logiki (nie DB).
    Używaj przy tworzeniu/edycji użytkownika, przed db.session.commit().
    """
    if user.role in {"staff", "admin"} and (not user.name or not user.surname):
        raise ValueError("Użytkownik z rolą staff/admin musi mieć uzupełnione name i surname.")
