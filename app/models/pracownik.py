from flask_login import UserMixin
from werkzeug.security import check_password_hash
from app.extensions import db


class Pracownik(UserMixin, db.Model):
    __tablename__ = "pracownicy"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    surname = db.Column(db.String(120))
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="staff")  # staff|client|admin

    def get_id(self):
        return str(self.id)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_staff(self) -> bool:
        return (self.role or "").lower() in ("staff", "admin")

    @property
    def is_client(self) -> bool:
        return (self.role or "").lower() == "client"