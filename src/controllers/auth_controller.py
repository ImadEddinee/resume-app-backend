import jwt
from flask import Blueprint, request, session, jsonify
from datetime import datetime, timedelta  # Import datetime class directly
from functools import wraps
from flask_bcrypt import generate_password_hash, check_password_hash
from src.models.user_model import User

auth_controller = Blueprint('auth_controller', __name__)

secret = "PHhV7HLc7I7-UWdh"


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('token')

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, secret, algorithms=['HS256'])

        except:
            return jsonify({'error': 'Token is invalid'}), 401

        return func(*args, **kwargs)

    return decorated


@auth_controller.route("/public")
def public():
    return jsonify({'message': 'Anyone can view this'})


@auth_controller.route("/auth", methods=["GET"])
@token_required
def private():
    return jsonify({'message': 'Only authorized users can view this'})


@auth_controller.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                session['logged_in'] = True
                token = jwt.encode({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'exp': datetime.now() + timedelta(days=2)
                }, secret, algorithm='HS256')
                return jsonify({'token': token})
            else:
                return jsonify({'error': 'Invalid username or password'}), 401
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
