import base64
import os
import uuid
from datetime import datetime, timedelta
from io import BytesIO
import nltk
import spacy
nltk.download('stopwords')
spacy.load('en_core_web_sm')
from pyresparser import ResumeParser
import pandas as pd
from flask import Blueprint, jsonify, request, send_file, send_from_directory
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy import and_, func
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
from src.models.education_model import Education
from src.models.experience_model import Experience
from src.models.role_model import Role
from src.models.skill_model import Skill
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
        users_count = User.query.filter_by(is_intern=1).count()
    elif user_type == 'extern':
        users_count = User.query.filter_by(is_extern=1).count()
    elif user_type == 'all':
        users_count = User.query.count()
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


@user_controller.route('users/chart', methods=['POST'])
def get_data_for_chart():

    chart_entry_formation = request.json.get('educationFormation', [])
    chart_entry_position = request.json.get('positions', [])
    chart_entry_skills = request.json.get('skills', [])

    print(chart_entry_formation,chart_entry_position,chart_entry_skills)

    education_counts = (
        Education.query
        .filter(Education.degree_title.in_(chart_entry_formation))
        .group_by(Education.degree_title)
        .with_entities(Education.degree_title, func.count().label('count'))
        .all()
    )

    formation_result = [{"degree_title": entry.degree_title, "count": entry.count} for entry in education_counts]

    position_counts = (
        BasicInfo.query
        .filter(BasicInfo.occupation.in_(chart_entry_position))
        .group_by(BasicInfo.occupation)
        .with_entities(BasicInfo.occupation, func.count().label('count'))
        .all()
    )

    position_result = [{"position_title": entry.occupation, "count": entry.count} for entry in position_counts]

    skill_counts = (
        Skill.query
        .filter(Skill.name.in_(chart_entry_skills))
        .group_by(Skill.name)
        .with_entities(Skill.name, func.count().label('count'))
        .all()
    )

    skill_result = [{"skill_title": entry.name, "count": entry.count} for entry in skill_counts]


    return jsonify({
        "formation": formation_result,
        "position": position_result,
        "skill": skill_result
    })





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



@user_controller.route('upload-resumes/interns', methods=['POST'])
def upload_resumes_for_interns():
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
        print(unique_filename)
        file.save(unique_filename)
        data = ResumeParser(unique_filename).get_extracted_data()
        print(data)
        file_paths.append(unique_name)
        skills = data.get('skills', [])
        new_user = User(
            is_intern=1,
            is_extern=0,
            has_resume=1,
            enabled=0,
        )
        db.session.add(new_user)
        db.session.commit()

        new_basic_info = BasicInfo(
            first_name=unique_name.split("keybr")[1],
            occupation="Dev",
            user_id=new_user.id
        )
        db.session.add(new_basic_info)
        db.session.commit()

        for skill_name in skills:
            new_skill = Skill(
                name=skill_name,
                user_id=new_user.id
            )
            db.session.add(new_skill)

        db.session.commit()

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


@user_controller.route('/users/occupations', methods=['POST'])
def get_internal_users_based_on_position():
    try:
        data = request.get_json()

        # Assuming 'selectedPosts' is a list of selected positions
        selected_posts = data.get('selectedPosts', [])

        print(selected_posts)

        # Query users based on the selected positions
        users = db.session.query(User).join(BasicInfo).filter(BasicInfo.occupation.in_(selected_posts)).all()
        print(users)
        # You can customize the response based on your needs
        user_list = []
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
            user_list.append(user_dict)

        return jsonify({'users': user_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_controller.route('/users/skills', methods=['POST'])
def get_internal_users_based_on_skills():
    try:
        data = request.get_json()

        # Assuming 'selectedPosts' is a list of selected positions
        selected_skills = data.get('skills', [])

        print(selected_skills)

        # Query users based on the selected positions
        users = db.session.query(User).join(Skill).filter(Skill.name.in_(selected_skills)).all()

        # You can customize the response based on your needs
        user_list = []
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
            user_list.append(user_dict)

        return jsonify({'users': user_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_controller.route('/users/degree-title', methods=['POST'])
def get_internal_users_based_on_education():
    try:
        data = request.get_json()

        # Assuming 'selectedPosts' is a list of selected positions
        selected_degree_titles = data.get('degreeTitle', [])

        print(selected_degree_titles)

        # Query users based on the selected positions
        users = db.session.query(User).join(Education).filter(Education.degree_title.in_(selected_degree_titles)).all()

        # You can customize the response based on your needs
        user_list = []
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
            user_list.append(user_dict)

        return jsonify({'users': user_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@user_controller.route('/users/project-name', methods=['POST'])
def get_internal_users_based_on_project_name():
    try:
        data = request.get_json()

        # Assuming 'selectedPosts' is a list of selected positions
        selected_project_name = data.get('projectName', [])

        print(selected_project_name)

        # Query users based on the selected positions
        users = db.session.query(User).join(Experience).filter(Experience.project_name.in_(selected_project_name)).all()

        # You can customize the response based on your needs
        user_list = []
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
            user_list.append(user_dict)

        return jsonify({'users': user_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@user_controller.route('/users/excel-data', methods=['POST'])
def export_excel_data():
    try:
        data = request.get_json()

        # Assuming 'selectedPosts' is a list of selected positions
        selected_ids = data.get('ids', [])

        print(selected_ids)

        users = db.session.query(User).filter(User.id.in_(selected_ids)).all()

        print(users)

        # Create a Pandas DataFrame from the user data
        user_data = {
            "ID": [user.id for user in users],
            "username": [user.username for user in users],
            "Email": [user.email for user in users],
        }

        df = pd.DataFrame(user_data)

        # Create an in-memory Excel file
        excel_output = BytesIO()

        with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='User Data', index=False)

        excel_output.seek(0)

        # Send the Excel file back to the frontend
        return send_file(
            excel_output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='user_data.xlsx'
        )

    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while processing the request"}), 500


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
        enabled=1,
        roles=[admin_role, user_role]  # Associate roles with the user
    )

    db.session.add(new_user)
    db.session.commit()

    # Access the user's ID
    user_id = new_user.id

    # Create BasicInfo instance and associate it with the user
    new_basic_info = BasicInfo(
        first_name="imad",
        last_name="eddine",
        age=20,
        occupation="Dev",
        user_id=user_id
    )

    db.session.add(new_basic_info)
    db.session.commit()

    new_contact = Contact(
        email="imad@gmail.com",
        phone_number="0876384768",
        user_id=user_id
    )

    db.session.add(new_contact)
    db.session.commit()

    new_skill = Skill(
        name="Java",
        user_id=user_id
    )

    db.session.add(new_skill)
    db.session.commit()

    new_education = Education(
        degree_title="Licence",
        user_id=user_id
    )

    db.session.add(new_education)
    db.session.commit()

    new_education = Education(
        degree_title="Master",
        user_id=user_id
    )

    db.session.add(new_education)
    db.session.commit()

    new_experience = Experience(
        project_name="Forewriter",
        user_id=user_id
    )

    db.session.add(new_experience)
    db.session.commit()

    new_experience = Experience(
        project_name="Portnet",
        user_id=user_id
    )

    db.session.add(new_experience)
    db.session.commit()

    # """""""""""""""""""""""""""""""""""""""""""""""""

    admin_role = Role(name='admin')
    user_role = Role(name='user')

    # Create a user and associate roles
    new_user = User(
        username='amine',
        password=generate_password_hash("123456"),
        email='email@gmail.com',
        is_intern=1,
        is_extern=0,
        enabled=1,
        roles=[admin_role, user_role]  # Associate roles with the user
    )

    db.session.add(new_user)
    db.session.commit()

    # Access the user's ID
    user_id = new_user.id

    # Create BasicInfo instance and associate it with the user
    new_basic_info = BasicInfo(
        first_name="imad",
        last_name="eddine",
        age=20,
        occupation="Manager",
        user_id=user_id
    )

    db.session.add(new_basic_info)
    db.session.commit()

    new_contact = Contact(
        email="amine@gmail.com",
        phone_number="0976384768",
        user_id=user_id
    )

    db.session.add(new_contact)
    db.session.commit()

    new_skill = Skill(
        name="PHP",
        user_id=user_id
    )

    db.session.add(new_skill)
    db.session.commit()

    new_education = Education(
        degree_title="Licence",
        user_id=user_id
    )

    db.session.add(new_education)
    db.session.commit()

    new_education = Education(
        degree_title="Master",
        user_id=user_id
    )

    db.session.add(new_education)
    db.session.commit()

    new_education = Education(
        degree_title="Ingénieur",
        user_id=user_id
    )

    db.session.add(new_education)
    db.session.commit()

    new_experience = Experience(
        project_name="Forewriter",
        user_id=user_id
    )

    db.session.add(new_experience)
    db.session.commit()

    return "Data Initialized"
