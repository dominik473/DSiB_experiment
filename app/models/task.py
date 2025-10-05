from datetime import datetime
from app.extensions import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created_by_id  = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="RESTRICT"), nullable=False, index=True)
    created_by     = db.relationship("User", foreign_keys=[created_by_id])

    assigned_to_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="RESTRICT"), nullable=False, index=True)
    assignee       = db.relationship("User", foreign_keys=[assigned_to_id])

    text = db.Column(db.String(400), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False, index=True)
    due_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
