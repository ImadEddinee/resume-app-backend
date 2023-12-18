import base64
import os
import uuid

from flask import Blueprint, jsonify, send_file

from database import db
from src.models.basic_info_model import BasicInfo

basic_info_controller = Blueprint('basic_info_controller', __name__)


@basic_info_controller.route("users/<int:user_id>/basic-infos")
def get_user_basic_info(user_id):
    basic_info = BasicInfo.query.filter_by(user_id=user_id).first()
    if not basic_info:
        return {}
    else:
        basic_info_dict = {
            "id": basic_info.id,
            "firstName": basic_info.first_name,
            "lastName": basic_info.last_name,
            "age": basic_info.age,
            "socialStatus": basic_info.social_status,
            "occupation": basic_info.occupation,
            "yearsOfExp": basic_info.years_of_exp,
            "birthDate": basic_info.birth_date,
            "picture": basic_info.resume_picture,
            "userId": user_id,
        }
    return basic_info_dict


@basic_info_controller.route("get-image/<int:user_id>", methods=['GET'])
def get_image(user_id):
    basic_info = BasicInfo.query.filter_by(user_id=user_id).first()
    if not basic_info or not basic_info.picture:
        return {}


    current_directory = os.getcwd()
    images_folder = os.path.join(current_directory, 'images')
    image_path = os.path.join(images_folder, basic_info.picture)

    # Use Flask's send_file function to send the image as a response
    return send_file(image_path, mimetype='image/png')


@basic_info_controller.route("basic-infos", methods=['POST'])
def create_or_update_basic_info_details(basic_info, user_id):
    basic_info_db = BasicInfo.query.filter_by(user_id=user_id).first()
    picture_path = False
    unique_name = ''
    if (basic_info.get('picture') != ''):
        current_directory = os.getcwd()

        # Create a folder named 'resumes' in the current directory if it doesn't exist
        images_folder = os.path.join(current_directory, 'images')
        if not os.path.exists(images_folder):
            os.makedirs(images_folder)

        base64_data = basic_info.get('picture')

        base64_data_padded = base64_data + '=' * (4 - len(base64_data) % 4)
        sanitized_string = base64_data_padded.replace('-', '+').replace('_', '/')
        image_data = base64.b64decode(sanitized_string)

        unique_name = str(uuid.uuid4())
        unique_filename = os.path.join(images_folder, unique_name)
        picture_path = True

        with open(unique_filename, 'wb') as f:
            f.write(image_data)

    if basic_info_db:
        basic_info_db.first_name = basic_info.get('firstName', basic_info_db.first_name)
        basic_info_db.last_name = basic_info.get('lastName', basic_info_db.last_name)
        basic_info_db.age = basic_info.get('age', basic_info_db.age)
        basic_info_db.social_status = basic_info.get('socialStatus', basic_info_db.social_status)
        basic_info_db.occupation = basic_info.get('occupation', basic_info_db.occupation)
        basic_info_db.years_of_exp = basic_info.get('yearsOfExp', basic_info_db.years_of_exp)
        basic_info_db.birth_date = basic_info.get('birthDate', basic_info_db.birth_date)
        if (picture_path):
            basic_info_db.picture = unique_name
    else:
        basic_info_db = BasicInfo(first_name=basic_info.get('firstName'),
                               last_name=basic_info.get('lastName'),
                               age=basic_info.get('age'),
                               social_status=basic_info.get('socialStatus'),
                               occupation=basic_info.get('occupation'),
                               years_of_exp=basic_info.get('yearsOfExp'),
                               birth_date=basic_info.get('birthDate'),
                               picture=unique_name,
                               user_id=user_id)
        db.session.add(basic_info_db)
    db.session.commit()


