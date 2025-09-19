from datetime import datetime
from app.extensions import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignee_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    text = db.Column(db.String(400), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    due_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
