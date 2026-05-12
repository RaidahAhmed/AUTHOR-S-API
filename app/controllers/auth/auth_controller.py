# Storing all functions to be used for the user authentication process

from flask import Blueprint, request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK
import validators
from app.models.users import User
from app.extensions import db, bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# user registration

@auth.route('/register', methods=['POST'])
def register_user():
    data = request.json
    print("Full JSON data:", data)
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    contact = data.get('contact')
    email = data.get('email')
    user_type = data.get('user_type')
    password = data.get('password')
    biography = data.get('biography', '') if user_type == 'author' else ''
    print("Extracted user_type:", user_type)
    print("Extracted biography:", repr(biography))

# validations of the incoming request
    if not first_name or not last_name or not contact or not password or not email:
        return jsonify({"error": "All Fields are Required"}), HTTP_400_BAD_REQUEST
    if user_type == 'author' and not biography:
        return jsonify({"error": "Enter your author biography"}), HTTP_400_BAD_REQUEST
    if len(password) < 8:
        return jsonify({"error": "Password is too short"}), HTTP_400_BAD_REQUEST
    if not validators.email(email):
        return jsonify({"error": "Email is not valid"}), HTTP_400_BAD_REQUEST
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error": "Email address already in use"}), HTTP_409_CONFLICT
    if User.query.filter_by(contact=contact).first() is not None:
        return jsonify({"error": "Contact already in use"}), HTTP_409_CONFLICT

    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')  # hashing the password
        # creating a new user:
        print("creating user with user_type:", user_type)
        new_user = User(first_name=first_name, last_name=last_name, password=hashed_password,
                        email=email, contact=contact, biography=biography, user_type=user_type)
        print("after creation:", new_user.user_type)
        print("user obj bio:", new_user.biography)
        db.session.add(new_user)
        db.session.commit()
        # username
        username = new_user.get_full_name()
        return jsonify({'message': f"{username or 'User'} has been successfully created as an {new_user.user_type or 'author'}",
                        'user': {
                            "id": new_user.id,
                            "first_name": new_user.first_name,
                            "last_name": new_user.last_name,
                            "email": new_user.email,
                            "contact": new_user.contact,
                            "biography": new_user.biography,
                            "user_type": new_user.user_type,
                            "created at": new_user.created_at.strftime("%A, %d %B %Y %H:%M:%S GMT") if new_user.created_at else None
                        }}), HTTP_201_CREATED
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


#user login
@auth.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    try:
        if not password or not email:
            return jsonify({'message':'Email and Password are required'}),HTTP_400_BAD_REQUEST
        user = User.query.filter_by(email=email).first()

        if user:
            is_correct_password = bcrypt.check_password_hash(user.password, password)
            if is_correct_password:
                access_token = create_access_token(identity=str(user.id))
                refresh_token = create_refresh_token(identity=str(user.id))
                return jsonify({'user':{
                    'id': user.id,
                    'username': user.get_full_name(),
                    'email': user.email,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user_type': user.user_type
                }, 'message': 'You have successfully logged into your account!'
                }), HTTP_200_OK
            else:
                return jsonify({'message':'Invalid password'}),HTTP_401_UNAUTHORIZED
        else:
            return jsonify({'message':'Invalid email address'}),HTTP_401_UNAUTHORIZED

    except Exception as e:
        return jsonify ({'error':str(e)}),HTTP_500_INTERNAL_SERVER_ERROR


@auth.route("token/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token':access_token})