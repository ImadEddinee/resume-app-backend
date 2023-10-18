from flask import Flask
from src.controllers.auth_controller import auth_controller
from src.controllers.basic_info_controller import basic_info_controller
from src.controllers.contact_controller import contact_controller
from src.controllers.education_controller import education_controller
from src.controllers.experience_controller import experience_controller
from src.controllers.skill_controller import skill_controller
from src.controllers.language_controller import language_controller
from database import db, protocol, db_host, db_name, db_user, db_password

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"{protocol}://{db_user}:{db_password}@{db_host}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Registering various API endpoints
app.register_blueprint(auth_controller, url_prefix="/api/v1/auth")
app.register_blueprint(basic_info_controller, url_prefix="/api/v1/")
app.register_blueprint(contact_controller, url_prefix="/api/v1/")
app.register_blueprint(education_controller, url_prefix="/api/v1/")
app.register_blueprint(experience_controller, url_prefix="/api/v1/")
app.register_blueprint(skill_controller, url_prefix="/api/v1/")
app.register_blueprint(language_controller, url_prefix="/api/v1/")


def setup_db():
    db.init_app(app)
    from src.models.user_model import User
    from src.models.role_model import Role
    from src.models.basic_info_model import BasicInfo
    from src.models.contact_model import Contact
    from src.models.education_model import Education
    from src.models.experience_model import Experience
    from src.models.experience_action_model import ExperienceAction
    from src.models.skill_model import Skill
    from src.models.language_model import Language

    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    setup_db()
    app.run()
