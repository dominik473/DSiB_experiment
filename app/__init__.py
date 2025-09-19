import os
from flask import Flask
from dotenv import load_dotenv
from .extensions import db, migrate, login_manager
from .blueprints.public import bp as public_bp
from .blueprints.auth import bp as auth_bp
from .blueprints.staff_panel import bp as staff_bp
from .blueprints.client_portal import bp as client_bp
from .cli import register_cli

def create_app(config_object="config.DevConfig"):
    app = Flask(__name__, instance_relative_config=True, static_folder="static", template_folder="templates")
    app.config.from_object(config_object)
    app.config["CALENDAR_ID_1"] = os.getenv("CALENDAR_ID_1")
    app.config["CALENDAR_ID_2"] = os.getenv("CALENDAR_ID_2")
    app.config["CALENDAR_ID_3"] = os.getenv("CALENDAR_ID_3")
    app.config["CALENDAR_ID_EDITABLE"] = os.getenv("CALENDAR_ID_EDITABLE")



    # Upewnij się, że katalog instance istnieje (dla SQLite)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Ext
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    register_cli(app)

    # Blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(staff_bp, url_prefix="/staff")
    app.register_blueprint(client_bp, url_prefix="/client")

    return app
