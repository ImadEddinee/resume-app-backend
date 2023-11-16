from flask import Blueprint, jsonify

from database import db
from src.models.basic_info_model import BasicInfo

basic_info_controller = Blueprint('basic_info_controller', __name__)


@basic_info_controller.route("users/<int:user_id>/basic-infos")
def get_user_basic_info(user_id):
    basic_info = BasicInfo.query.filter_by(user_id=user_id).first()
    basic_info_dict = {
        "id": basic_info.id,
        "firstName": basic_info.first_name,
        "lastName": basic_info.last_name,
        "age": basic_info.age,
        "socialStatus": basic_info.social_status,
        "occupation": basic_info.occupation,
        "yearsOfExp": basic_info.years_of_exp,
        "birthDate": basic_info.birth_date,
        "userId": user_id,
    }
    return basic_info_dict


@basic_info_controller.route("basic-infos", methods=['POST'])
def create_or_update_basic_info_details(basic_info, user_id):
    basic_info_db = BasicInfo.query.filter_by(user_id=user_id).first()
    if basic_info_db:
        basic_info_db.first_name = basic_info['firstName']
        basic_info_db.last_name = basic_info['lastName']
        basic_info_db.age = basic_info['age']
        basic_info_db.social_status = basic_info['socialStatus']
        basic_info_db.occupation = basic_info['occupation']
        basic_info_db.years_of_exp = basic_info['yearsOfExp']
        basic_info_db.birth_date = basic_info['birthDate']
    else:
        basic_info_db = BasicInfo(first_name=basic_info['firstName'],
                               last_name=basic_info['lastName'],
                               age=basic_info['age'],
                               social_status=basic_info['socialStatus'],
                               occupation=basic_info['occupation'],
                               years_of_exp=basic_info['yearsOfExp'],
                               birth_date=basic_info['birthDate'],
                               user_id=user_id)
        db.session.add(basic_info_db)
    db.session.commit()
