import random
import string


from database import db
import jwt
from flask import Blueprint, request, session, jsonify, make_response
from datetime import datetime, timedelta
from functools import wraps
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.models.user_model import User


auth_controller = Blueprint('auth_controller', __name__)

secret = "PHhV7HLc7I7-UWdh"
refresh_secret = "RefreshSecretKey"  # Replace with your own secret key for refresh tokens


def auth_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            # Check if the header starts with "Bearer " and remove it
            if auth_header.startswith('Bearer '):
                token = auth_header[len('Bearer '):]
            else:
                token = auth_header
            data = jwt.decode(token, secret, algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 401

        return func(*args, **kwargs)

    return decorated

def auth_refresh_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Refresh token is missing'}), 401

        try:
            # Check if the header starts with "Bearer " and remove it
            if auth_header.startswith('Bearer '):
                refresh_token = auth_header[len('Bearer '):]
            else:
                refresh_token = auth_header

            # Decode the refresh token
            data = jwt.decode(refresh_token, secret, algorithms=['HS256'])

            # Add additional checks for the refresh token if needed

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Refresh token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Refresh token is invalid'}), 401

        return func(*args, **kwargs)

    return decorated



@auth_controller.route("/public")
def public():
    return jsonify({'message': 'Anyone can view this'})


@auth_controller.route("/", methods=["GET"])
@auth_required
def private():
    return jsonify({'message': 'Only authorized users can view this'})


@auth_controller.route('/info', methods=['GET'])
@auth_required
def login_info_api():
    """
    Get information about the currently logged in user
    """
    user = get_authenticated_user()

    if user:
        roles = [role.to_dict() for role in user.roles]
        response_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'enabled': user.enabled,
            'roles': roles  # Assuming user.roles is a list of roles
        }
        return make_response(jsonify(response_data))
    else:
        # Handle the case where the user is not found or not enabled
        return make_response(jsonify({'error': 'User not found or not enabled'}), 404)


@jwt_required()
def get_authenticated_user():
    """
    Get authentication token user identity and verify account is active
    """
    identity = get_jwt_identity()
    user = User.query.filter_by(id=identity).first()

    if user and user.enabled:
        return user
    else:
        print("User not Found or not Enabled")
        return None

@auth_controller.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username).first()
        if user:
            if user.enabled:
                if check_password_hash(user.password, password):
                    # Generate access token
                    access_token = jwt.encode({
                        'sub': user.id,
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'exp': datetime.now() + timedelta(days=2)
                    }, secret, algorithm='HS256')

                    # Generate refresh token
                    refresh_token = jwt.encode({
                        'id': user.id,
                        'exp': datetime.now() + timedelta(days=30)
                    }, refresh_secret, algorithm='HS256')

                    return jsonify({'accessToken': access_token, 'refreshToken': refresh_token})
                else:
                    return jsonify({'error': 'Mot de passe est incorrect.'}), 401
            else:
                return jsonify({'error': 'Le compte est désactivé.'}), 401
        else:
            return jsonify({'error': 'Nom d\'utilisateur est incorrect.'}), 401


@auth_controller.route("/refresh", methods=["POST"])
def refresh():
    if request.method == "POST":
        data = request.get_json()
        refresh_token = data.get('refresh_token')

        if not refresh_token:
            return jsonify({'error': 'Refresh token is missing'}), 401

        try:
            data = jwt.decode(refresh_token, refresh_secret, algorithms=['HS256'])

            # Generate a new access token
            new_access_token = jwt.encode({
                'id': data['id'],
                'exp': datetime.now() + timedelta(days=2)
            }, secret, algorithm='HS256')

            return jsonify({'access_token': new_access_token})
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Refresh token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Refresh token is invalid'}), 401


@auth_controller.route('/change-password', methods=['POST'])
def change_password():
    email = request.json.get('email')
    new_password = request.json.get('newPassword')
    confirm_new_password = request.json.get('confirmNewPassword')
    reset_code = request.json.get('resetCode')

    # Find the user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Verify the reset code and check if it is still valid
    if user.reset_code == reset_code and datetime.strptime(user.reset_code_expiration, '%Y-%m-%d %H:%M:%S.%f') > datetime.utcnow():
        # Check if the new password and confirmation match
        print(new_password,confirm_new_password)
        if new_password == confirm_new_password:
            # Update the user's password
            user.password = generate_password_hash(new_password)
            user.reset_code = None  # Clear the reset code
            user.reset_code_expiration = None  # Clear the reset code expiration
            db.session.commit()
            return jsonify({"message": "Password changed successfully"}), 200
        else:
            return jsonify({"error": "New password and confirmation do not match"}), 401
    else:
        return jsonify({"message": "Invalid reset code"}), 400





