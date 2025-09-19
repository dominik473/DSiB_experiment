from flask import Blueprint
bp = Blueprint("client", __name__, template_folder="../../templates/client_portal")
from . import routes  # noqa
