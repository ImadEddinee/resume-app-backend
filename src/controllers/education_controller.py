from flask import Blueprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import db, protocol, db_host, db_name, db_user, db_password
from src.models.education_model import Education

education_controller = Blueprint('education_controller', __name__)


@education_controller.route("users/<int:user_id>/educations")
def get_user_education(user_id):
    educations = Education.query.filter_by(user_id=user_id).all()
    education_info = [
        {
            "id": education.id,
            "degreeTitle": education.degree_title,
            "institution": education.institution,
            "startingYear": education.starting_year,
            "onGoing": education.ongoing,
            "graduatingYear": education.graduating_year,
            "userId": user_id,
        }
        for education in educations
    ]
    return education_info


@education_controller.route("educations", methods=['POST'])
def create_or_update_education_details(education, user_id):
    delete_education_infos_for_user(user_id)
    education_infos = []
    for educ_info in education:
        if educ_info['onGoing']:
            educ_info['onGoing'] = 1
        else:
            educ_info['onGoing'] = 0
        educ_info_db = Education(degree_title=educ_info['degreeTitle'],
                                 institution=educ_info['institution'],
                                 starting_year=educ_info['startingYear'],
                                 ongoing=educ_info['onGoing'],
                                 graduating_year=educ_info['graduatingYear'],
                                 user_id=user_id)
        education_infos.append(educ_info_db)
    db.session.add_all(education_infos)
    db.session.commit()


def delete_education_infos_for_user(user_id):
    engine = create_engine(f"{protocol}://{db_user}:{db_password}@{db_host}/{db_name}")
    Session = sessionmaker(bind=engine)
    session = Session()
    existing_education_infos = session.query(Education).filter_by(user_id=user_id).all()
    for educ_info in existing_education_infos:
        session.delete(educ_info)
    session.commit()
