import random
import string
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail, Message

from src.controllers.auth_controller import auth_controller
from src.controllers.user_controller import user_controller
from src.controllers.basic_info_controller import basic_info_controller
from src.controllers.contact_controller import contact_controller
from src.controllers.education_controller import education_controller
from src.controllers.experience_controller import experience_controller
from src.controllers.skill_controller import skill_controller
from src.controllers.language_controller import language_controller
from database import db, protocol, db_host, db_name, db_user, db_password
from src.models.user_model import User

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "imadhajali66@gmail.com"
app.config['MAIL_PASSWORD'] = "nisx bkzl gxke qcop"
mail = Mail(app)


def send_email(recipient, reset_code):
    with app.app_context():
        msg = Message("Password Reset Code", recipients=[recipient])
        msg.body = f"Your password reset code is: {reset_code}"
        msg.sender = 'imadhajali66@gmail.com'
        mail.send(msg)

CORS(app)

def generate_reset_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@auth_controller.route('/reset-password', methods=['POST'])
def request_password_reset():
    print(12)
    email = request.json.get('email')

    # Find the user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Generate and store the reset code
    reset_code = generate_reset_code()
    user.reset_code = reset_code
    user.reset_code_expiration = datetime.utcnow() + timedelta(minutes=30)
    db.session.commit()

    # Send the reset code via email
    send_email(user.email, reset_code)

    return jsonify({"message": "Reset code sent successfully"}), 200

@auth_controller.route('/verify-reset-code', methods=['POST'])
def verify_reset_code():
    email = request.json.get('email')
    reset_code = request.json.get('reset_code')

    # Find the user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Verify the reset code
    if user.reset_code == reset_code and datetime.strptime(user.reset_code_expiration, '%Y-%m-%d %H:%M:%S.%f') > datetime.utcnow():
        return jsonify({"message": "Reset code is valid"}), 200
    else:
        return jsonify({"message": "Invalid reset code"}), 400

app.config['SQLALCHEMY_DATABASE_URI'] = f"{protocol}://{db_user}:{db_password}@{db_host}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'PHhV7HLc7I7-UWdh'
app.config['JWT_SECRET_KEY'] = 'PHhV7HLc7I7-UWdh'
jwt = JWTManager(app)

# Registering various API endpoints
app.register_blueprint(auth_controller, url_prefix="/api/v1/auth")
app.register_blueprint(user_controller, url_prefix="/api/v1/")
app.register_blueprint(basic_info_controller, url_prefix="/api/v1/")
app.register_blueprint(contact_controller, url_prefix="/api/v1/")
app.register_blueprint(education_controller, url_prefix="/api/v1/")
app.register_blueprint(experience_controller, url_prefix="/api/v1/")
app.register_blueprint(skill_controller, url_prefix="/api/v1/")
app.register_blueprint(language_controller, url_prefix="/api/v1/")


def setup_db():
    db.init_app(app)
    from src.models.user_model import User
    from src.models.role_model import Role
    from src.models.basic_info_model import BasicInfo
    from src.models.contact_model import Contact
    from src.models.education_model import Education
    from src.models.experience_model import Experience
    from src.models.experience_action_model import ExperienceAction
    from src.models.skill_model import Skill
    from src.models.language_model import Language

    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    setup_db()
    # send_email()
    app.run()
