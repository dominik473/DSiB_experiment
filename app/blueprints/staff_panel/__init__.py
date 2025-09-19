from flask import Blueprint
bp = Blueprint("staff", __name__, template_folder="../../templates/staff_panel")
from . import routes  # noqa
