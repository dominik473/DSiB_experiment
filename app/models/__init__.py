# app/models/__init__.py
# Importy po to, by Alembic/Flask widziały modele (target_metadata = db.metadata)
from app.extensions import db  # eksport wspólnego db

# Twoje istniejące modele:
from .user import User        # jeżeli masz
from .task import Task        # jeżeli masz
from .note import Note        # jeżeli masz

# Rdzeń, który właśnie porządkujemy:
from .core import Klient, Inwestycja

__all__ = [
    "db",
    "User", "Task", "Note",
    "Klient", "Inwestycja",
]
