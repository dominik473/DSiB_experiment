# app/__init__.py
import os
from flask import Flask
from dotenv import load_dotenv

from app.extensions import db, migrate, login_manager
from app.cli import register_cli


def create_app(config_object="config.DevConfig"):
    load_dotenv()

    flask_app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="static",
        template_folder="templates",
    )
    flask_app.config.from_object(config_object)

    # Google Calendar (z .env)
    flask_app.config["CALENDAR_ID_1"] = os.getenv("CALENDAR_ID_1")
    flask_app.config["CALENDAR_ID_2"] = os.getenv("CALENDAR_ID_2")
    flask_app.config["CALENDAR_ID_3"] = os.getenv("CALENDAR_ID_3")
    flask_app.config["CALENDAR_ID_EDITABLE"] = os.getenv("CALENDAR_ID_EDITABLE")

    os.makedirs(flask_app.instance_path, exist_ok=True)

    # Ext
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    login_manager.init_app(flask_app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    register_cli(flask_app)

    # Wczytaj modele, żeby Alembic widział metadata
    import app.models  # noqa: F401

    # Import blueprintów DOPIERO teraz (lazy import)
    from app.blueprints.public import bp as public_bp
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.staff_panel import bp as staff_bp
    from app.blueprints.client_portal import bp as client_bp

    # Rejestracja BP NA INSTANCJI (flask_app), NIE na pakiecie 'app'
    flask_app.register_blueprint(public_bp)
    flask_app.register_blueprint(auth_bp, url_prefix="/auth")
    flask_app.register_blueprint(staff_bp, url_prefix="/staff")
    flask_app.register_blueprint(client_bp, url_prefix="/client")

    return flask_app
