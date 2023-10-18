from flask import Blueprint

contact_controller = Blueprint('contact_controller', __name__)


@contact_controller.route("/signup")
def signup():
    return "signup"
