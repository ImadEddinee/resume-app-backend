from flask import Blueprint

skill_controller = Blueprint('skill_controller', __name__)


@skill_controller.route("/signup")
def signup():
    return "signup"
