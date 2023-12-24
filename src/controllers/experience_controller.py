from flask import Blueprint

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import db, protocol, db_host, db_name, db_user, db_password
from src.models.experience_action_model import ExperienceAction
from src.models.experience_model import Experience

experience_controller = Blueprint('experience_controller', __name__)


@experience_controller.route("users/<int:user_id>/experiences")
def get_user_experience(user_id):
    experiences = Experience.query.filter_by(user_id=user_id).all()
    if not experiences:
        return []
    else:
        experience_ids = [exp.id for exp in experiences]
        experience_actions = (db.session.query(ExperienceAction)
                          .join(Experience, ExperienceAction.experience_id == Experience.id)
                          .filter(Experience.id.in_(experience_ids)).all())
        experience_info = []
        for exp in experiences:
            additional_info = [
                {"id": action.id, "content": action.action} for action in experience_actions if
                action.experience_id == exp.id
            ]
            experience_info.append({
                "id": exp.id,
                "jobTitle": exp.job_title,
                "internJobTitle": exp.project_name,
                "company": exp.company,
                "startingYear": exp.starting_year,
                "onGoing": exp.ongoing,
                "endingYear": exp.ending_year,
                "role": exp.role,
                "additionalInfo": additional_info,
                "userId": user_id,
            })
    return experience_info


@experience_controller.route("experiences", methods=['POST'])
def create_or_update_experience_details(experience, user_id):
    delete_experience_actions(user_id)
    delete_experience_for_user(user_id)
    experience_infos = []
    for exp_info in experience:
        exp_actions = exp_info['additionalInfo']
        if exp_info['onGoing']:
            exp_info['onGoing'] = 1
        else:
            exp_info['onGoing'] = 0
        exp_info_db = Experience(job_title=exp_info['jobTitle'],
                                 company=exp_info['company'],
                                 starting_year=exp_info['startingYear'],
                                 ongoing=exp_info['onGoing'],
                                 ending_year=exp_info['endingYear'],
                                 role=exp_info['role'],
                                 user_id=user_id,
                                 actions=[ExperienceAction(action=action['content']) for action in exp_actions])
        experience_infos.append(exp_info_db)
    db.session.add_all(experience_infos)
    db.session.commit()



def delete_experience_actions(user_id):
    experiences = Experience.query.filter_by(user_id=user_id).all()
    experience_ids = [exp.id for exp in experiences]
    experience_actions = (db.session.query(ExperienceAction)
                          .join(Experience, ExperienceAction.experience_id == Experience.id)
                          .filter(Experience.id.in_(experience_ids)).all())
    for exp_action in experience_actions:
        db.session.delete(exp_action)
    db.session.commit()


def delete_experience_for_user(user_id):
    engine = create_engine(f"{protocol}://{db_user}:{db_password}@{db_host}/{db_name}")
    Session = sessionmaker(bind=engine)
    session = Session()
    existing_experience_infos = session.query(Experience).filter_by(user_id=user_id).all()
    for exp_info in existing_experience_infos:
        session.delete(exp_info)
    session.commit()
