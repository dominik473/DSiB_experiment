from flask import Blueprint
bp = Blueprint("auth", __name__, template_folder="../../templates/auth")
from . import routes_pracownik as routes  # noqa