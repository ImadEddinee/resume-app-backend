from flask import Blueprint

auth_controller = Blueprint('auth_controller', __name__)


@auth_controller.route("/signup")
def signup():
    return "signup"
