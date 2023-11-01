from flask import Blueprint, jsonify, request

from database import db
from src.controllers.basic_info_controller import get_user_basic_info, create_or_update_basic_info_details
from src.controllers.contact_controller import get_user_contact, create_or_update_contact_details
from src.controllers.education_controller import get_user_education, create_or_update_education_details
from src.controllers.experience_controller import get_user_experience, create_or_update_experience_details
from src.controllers.language_controller import get_user_language, create_or_update_language_details
from src.controllers.skill_controller import get_user_skills, create_or_update_skill_details
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
