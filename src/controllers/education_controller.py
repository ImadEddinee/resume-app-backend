from flask import Blueprint

education_controller = Blueprint('education_controller', __name__)


@education_controller.route("/signup")
def signup():
    return "signup"
