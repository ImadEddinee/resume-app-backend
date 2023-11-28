from flask import Blueprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import db, protocol, db_host, db_name, db_user, db_password
from src.models.language_model import Language

language_controller = Blueprint('language_controller', __name__)


@language_controller.route("users/<int:user_id>/languages")
def get_user_language(user_id):
    languages = Language.query.filter_by(user_id=user_id).all()
    if not languages:
        return {}
    else:
        language_info = [
            {
                "id": language.id,
                "language": language.language,
                "speak": language.speak,
                "read": language.read,
                "write": language.write,
                "userId": user_id,
            }
            for language in languages
        ]
    return language_info


@language_controller.route("languages", methods=['POST'])
def create_or_update_language_details(language, user_id):
    delete_language_infos_for_user(user_id)
    language_infos = []
    for lang_info in language:
        lang_info_db = Language(language=lang_info['language'],
                                speak=lang_info['speak'],
                                read=lang_info['read'],
                                write=lang_info['write'],
                                user_id=user_id)
        language_infos.append(lang_info_db)
    db.session.add_all(language_infos)
    db.session.commit()


def delete_language_infos_for_user(user_id):
    engine = create_engine(f"{protocol}://{db_user}:{db_password}@{db_host}/{db_name}")
    Session = sessionmaker(bind=engine)
    session = Session()
    existing_language_infos = session.query(Language).filter_by(user_id=user_id).all()
    for lang_info in existing_language_infos:
        session.delete(lang_info)
    session.commit()
