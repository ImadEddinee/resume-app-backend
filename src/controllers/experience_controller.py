from flask import Blueprint

experience_controller = Blueprint('experience_controller', __name__)


@experience_controller.route("/signup")
def signup():
    return "signup"
