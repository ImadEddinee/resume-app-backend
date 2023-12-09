from flask import Blueprint, jsonify, request
from flask_bcrypt import generate_password_hash
from database import db
from src.controllers.basic_info_controller import get_user_basic_info, create_or_update_basic_info_details
from src.controllers.contact_controller import get_user_contact, create_or_update_contact_details
from src.controllers.education_controller import get_user_education, create_or_update_education_details
from src.controllers.experience_controller import get_user_experience, create_or_update_experience_details
from src.controllers.language_controller import get_user_language, create_or_update_language_details
from src.controllers.skill_controller import get_user_skills, create_or_update_skill_details
from src.models.role_model import Role
from src.models.user_model import User

user_controller = Blueprint('user_controller', __name__)


@user_controller.route("users/<int:user_id>")
def get_user_resume_details(user_id):
    user_data = {
        "basicInfo": get_user_basic_info(user_id),
        "contactInfo": get_user_contact(user_id),
        "skillsInfo": get_user_skills(user_id),
        "educationInfo": get_user_education(user_id),
        "experienceInfo": get_user_experience(user_id),
        "languageInfo": get_user_language(user_id)
    }
    return jsonify(user_data)


@user_controller.route("users/<int:user_id>", methods=['POST'])
def create_or_update_user_resume_details(user_id):
    create_or_update_basic_info_details(request.json['basicInfo'], user_id)
    create_or_update_contact_details(request.json['contactInfo'], user_id)
    create_or_update_skill_details(request.json['skillsInfo'], user_id)
    create_or_update_education_details(request.json['educationInfo'], user_id)
    create_or_update_experience_details(request.json['experienceInfo'], user_id)
    create_or_update_language_details(request.json['languageInfo'], user_id)
    return 'Done'


@user_controller.route("users", methods=['GET'])
def users_details():
    user_type = request.args.get('type')
    if user_type == 'intern':
        users_count = User.query.filter_by(is_intern=1).count()
    elif user_type == 'extern':
        users_count = User.query.filter_by(is_extern=1).count()
    elif user_type == 'all':
        users_count = User.query.filter_by(has_resume=1).count()
    else:
        users_count = 0
    return str(users_count)

@user_controller.route("initializer")
def init_data():
    admin_role = Role(name='admin')
    user_role = Role(name='user')

    # Create a user and associate roles
    new_user = User(
        username='example_user',
        password= generate_password_hash("123456"),
        email='example@email.com',
        is_intern=1,
        is_extern=0,
        has_resume=1,
        roles=[admin_role, user_role]  # Associate roles with the user
    )

    db.session.add(new_user)
    db.session.commit()
    return "Data Initialized"
