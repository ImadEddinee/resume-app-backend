import base64
import os
import uuid
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, send_file, send_from_directory
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy import and_
from werkzeug.utils import secure_filename

from database import db
from src.controllers.auth_controller import auth_required
from src.controllers.basic_info_controller import get_user_basic_info, create_or_update_basic_info_details
from src.controllers.contact_controller import get_user_contact, create_or_update_contact_details
from src.controllers.education_controller import get_user_education, create_or_update_education_details
from src.controllers.experience_controller import get_user_experience, create_or_update_experience_details
from src.controllers.language_controller import get_user_language, create_or_update_language_details
from src.controllers.skill_controller import get_user_skills, create_or_update_skill_details
from src.models.basic_info_model import BasicInfo
from src.models.contact_model import Contact
from src.models.role_model import Role
from src.models.user_model import User

user_controller = Blueprint('user_controller', __name__)
SEPERATOR = "keybr"


@user_controller.route("users/<int:user_id>")
def get_user_resume_details(user_id):
    print(user_id)
    user_data = {
        "basicInfo": get_user_basic_info(user_id),
        "contactInfo": get_user_contact(user_id),
        "skillsInfo": get_user_skills(user_id),
        "educationInfo": get_user_education(user_id),
        "experienceInfo": get_user_experience(user_id),
        "languageInfo": get_user_language(user_id)
    }
    print(jsonify(user_data))
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


@user_controller.route("users/<int:user_id>/current-position")
def get_user_occupation(user_id):
    basic_info = BasicInfo.query.filter_by(user_id=user_id).first()
    return jsonify({'currentPosition': basic_info.occupation})


@user_controller.route("users", methods=['GET'])
@auth_required
def users_details():
    user_type = request.args.get('type')
    if user_type == 'extern':
        users = User.query.filter(and_(User.is_extern == 1, User.has_resume == 1)).all()
        # Convert User objects to dictionaries
        users_data = []
        for user in users:
            user_dict = {
                'id': user.id,
                'resume': user.resume,
                'createdAt': user.created_at
            }
            users_data.append(user_dict)

        return jsonify({'users': users_data})

    if user_type == 'intern':
        users = User.query.filter_by(is_intern=1).all()
        # Convert User objects to dictionaries
        users_data = []
        for user in users:
            basic_info = BasicInfo.query.filter_by(user_id=user.id).first()
            contact = Contact.query.filter_by(user_id=user.id).first()
            user_dict = {
                'id': user.id,
                "firstName": basic_info.first_name if basic_info else "-",
                "lastName": basic_info.last_name if basic_info else "-",
                "occupation": basic_info.occupation if basic_info else "-",
                "email": contact.email if contact else "-",
                "phoneNumber": contact.phone_number if contact else "-"
            }
            users_data.append(user_dict)

        return jsonify({'users': users_data})
    else:
        # Handle other cases if needed
        return jsonify({'message': 'Invalid user_type'})


@user_controller.route('users/download/<int:user_id>', methods=['GET'])
def download_resume(user_id):
    user = User.query.filter_by(id=user_id).first()
    resume_path = user.resume
    vqr = os.getcwd() + "\\resumes\\"
    print(vqr)
    print(resume_path)
    return send_from_directory(vqr, resume_path)


@user_controller.route("users/count", methods=['GET'])
@auth_required
def users_count():
    user_type = request.args.get('type')
    if user_type == 'intern':
        users_count = User.query.filter(and_(User.is_intern == 1, User.has_resume == 1)).count()
    elif user_type == 'extern':
        users_count = User.query.filter(and_(User.is_extern == 1, User.has_resume == 1)).count()
    elif user_type == 'all':
        users_count = User.query.filter_by(has_resume=1).count()
    elif user_type == 'intern_profiles':
        users_count = User.query.filter_by(is_intern=1).count()
    elif user_type == 'modified':
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        users_count = User.query.filter(
            User.has_resume == 1,
            (User.created_at >= one_week_ago) | (User.updated_at >= one_week_ago)
        ).count()
    else:
        users_count = 0
    return str(users_count)


@user_controller.route('upload-resumes', methods=['POST'])
def upload_resumes():
    # Get the current working directory (where the script is executed)
    current_directory = os.getcwd()

    # Create a folder named 'resumes' in the current directory if it doesn't exist
    resumes_folder = os.path.join(current_directory, 'resumes')
    if not os.path.exists(resumes_folder):
        os.makedirs(resumes_folder)

    # Get the list of uploaded files
    uploaded_files = request.files.getlist('resumes')
    print(uploaded_files)

    # Save each file to the 'resumes' folder with a unique name using uuid
    file_paths = []
    for file in uploaded_files:
        # Generate a unique filename using uuid
        unique_name = str(uuid.uuid4()) + SEPERATOR + file.filename
        unique_filename = os.path.join(resumes_folder, unique_name)
        file.save(unique_filename)
        file_paths.append(unique_name)

    for path in file_paths:
        new_user = User(
            is_intern=0,
            is_extern=1,
            has_resume=1,
            enabled=0,
            resume=path
        )
        db.session.add(new_user)

    db.session.commit()

    return jsonify({'message': 'Resumes uploaded successfully'})


@user_controller.route("users", methods=['POST'])
def update_user():
    data = request.get_json()
    print(data)
    user = User.query.get(data['id'])
    basic_info = BasicInfo.query.filter_by(user_id=data['id']).first()
    # Check which fields are present in the request and update accordingly
    if 'username' in data:
        username = data['username']
        user.username = username

    if 'email' in data:
        email = data['email']
        user.email = email

    if 'currentPosition' in data:
        current_position = data['currentPosition']
        basic_info.occupation = current_position

    if 'oldPassword' in data and 'newPassword' in data:
        old_password = data['oldPassword']
        new_password = data['newPassword']
        if check_password_hash(user.password, old_password):
            user.password = generate_password_hash(new_password)
        else:
            return jsonify({"error": "Incorrect old password"}), 400

    db.session.add(user)
    db.session.add(basic_info)
    db.session.commit()
    # Return a response indicating success or failure
    return jsonify({"message": "User updated successfully"})


@user_controller.route("users/<int:user_id>/picture", methods=['GET'])
def get_image(user_id):
    user = User.query.filter_by(id=user_id).first()


    images_folder = os.path.join(os.getcwd(), 'images')
    filename = os.path.join(images_folder, user.profile_picture)
    print(filename)


    return send_file(filename, mimetype='image/jpg')


@user_controller.route("users/<int:user_id>/picture", methods=['POST'])
def upload_profile_picture(user_id):
    user = User.query.filter_by(id=user_id).first()

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    current_directory = os.getcwd()

    images_folder = os.path.join(current_directory, 'images')

    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    if file:
        unique_name = str(uuid.uuid4()) + SEPERATOR + file.filename
        unique_filename = os.path.join(images_folder, unique_name)
        print(unique_filename)
        file.save(unique_filename)
        user.profile_picture = unique_filename
        db.session.commit()
        return jsonify({'message': 'File uploaded successfully'})



@user_controller.route("initializer")
def init_data():
    admin_role = Role(name='admin')
    user_role = Role(name='user')

    # Create a user and associate roles
    new_user = User(
        username='imad',
        password=generate_password_hash("123456"),
        email='imad.essa20@gmail.com',
        is_intern=1,
        is_extern=0,
        has_resume=1,
        roles=[admin_role, user_role]  # Associate roles with the user
    )

    db.session.add(new_user)
    db.session.commit()
    return "Data Initialized"
