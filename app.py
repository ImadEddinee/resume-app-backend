from flask import Flask
from src.controllers.auth_controller import auth_controller

app = Flask(__name__)

app.register_blueprint(auth_controller, url_prefix="/api/v1/auth")

if __name__ == "__main__":
    app.run()
