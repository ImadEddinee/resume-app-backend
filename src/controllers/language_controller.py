from flask import Blueprint

language_controller = Blueprint('language_controller', __name__)


@language_controller.route("/signup")
def signup():
    return "signup"
