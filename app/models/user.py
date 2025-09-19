from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="client")  # client/staff/admin

    def set_password(self, raw): self.password_hash = generate_password_hash(raw)
    def check_password(self, raw): return check_password_hash(self.password_hash, raw)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
