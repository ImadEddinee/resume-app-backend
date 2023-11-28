from flask import Blueprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.skill_model import Skill
from database import db, protocol, db_host, db_name, db_user, db_password

skill_controller = Blueprint('skill_controller', __name__)

@skill_controller.route("users/<int:user_id>/skills")
def get_user_skills(user_id):
    skills = Skill.query.filter_by(user_id=user_id).all()
    if not skills:
        return {}
    else:
        skills_info = [{"id": skill.id, "content": skill.name} for skill in skills]
    return skills_info


@skill_controller.route("skills", methods=['POST'])
def create_or_update_skill_details(skills, user_id):
    delete_all_skills_for_user(user_id)
    skill_objects = []
    for skill in skills:
        skill_db = Skill(name=skill['name'], user_id=user_id)
        skill_objects.append(skill_db)
    db.session.add_all(skill_objects)
    db.session.commit()


def delete_all_skills_for_user(user_id):
    engine = create_engine(f"{protocol}://{db_user}:{db_password}@{db_host}/{db_name}")
    Session = sessionmaker(bind=engine)
    session = Session()
    existing_skills = session.query(Skill).filter_by(user_id=user_id).all()
    for skill in existing_skills:
        session.delete(skill)
    session.commit()
