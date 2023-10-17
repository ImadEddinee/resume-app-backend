from flask import Flask
from src.controllers.auth_controller import auth_controller
from database import db, protocol, db_host, db_name, db_user, db_password

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"{protocol}://{db_user}:{db_password}@{db_host}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.register_blueprint(auth_controller, url_prefix="/api/v1/auth")


def setup_db():
    db.init_app(app)
    from src.models.basic_info_model import nnnnnnllllljjjjetttefehyInfo
    '''
    Uncomment to create tables
    with app.app_context():
        db.create_all()
    '''
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    setup_db()
    app.run()
