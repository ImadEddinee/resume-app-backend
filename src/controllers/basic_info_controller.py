from flask import Blueprint

basic_info_controller = Blueprint('basic_info_controller', __name__)


@basic_info_controller.route("/signup")
def signup():
    return "signup"
