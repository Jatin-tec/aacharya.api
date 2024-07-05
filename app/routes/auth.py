from flask import request, jsonify, Blueprint, redirect, url_for, session, current_app, session
from ..services.auth_service import create_user, get_user_by_email, verify_password
from ..utils.auth.parse_object import parse_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from urllib.parse import urlencode
from bson import ObjectId
import uuid
import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
def login_route():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    mongo = current_app.db["users"]
    user = get_user_by_email(email, mongo)
    
    if not user or not verify_password(user, password):
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=str(user["email"]))
    user = parse_user(user)
    return jsonify({
        "access_token": access_token,
        **user
    }), 200

@bp.route('/is_authenticated', methods=['GET'])
@jwt_required()
def is_authenticated():
    try:
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200
    except Exception as e:
        return jsonify({"msg": f"Unauthorized, {e}"}), 401

@bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    given_name = data.get("first_name")
    family_name = data.get("last_name")
    mongo = current_app.db["users"]

    if get_user_by_email(email, mongo):
        return jsonify({"msg": "User already exists"}), 400

    user = {
        "email": email,
        "verified_email": False,
        "sid": str(uuid.uuid4()),
        "name": f"{given_name} {family_name}",
        "given_name": given_name,
        "family_name": family_name,
        "picture": "",
        "password": password,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
        "last_login": datetime.datetime.now(),
        "is_active": True
    }

    user_id = create_user(user, mongo)
    return jsonify({"msg": "User created", "user_id": str(user_id)}), 200

@bp.route('/login/google')
def google_login():
    google = current_app.google
    return google.authorize(callback=url_for('auth.google_authorized', _external=True, _scheme='https'))


@bp.route('/login/google/authorized')
def google_authorized():
    google = current_app.google
    mongo = current_app.db["users"]
    CLIENT_URL = current_app.config["CLIENT_URL"]
    
    @google.tokengetter
    def get_google_oauth_token():
        return session.get('google_token')

    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return jsonify({"msg": "Access denied: reason={} error={}".format(
            request.args['error_reason'],
            request.args['error_description']
        )}), 400

    session['google_token'] = (response['access_token'], '')
    google_user_info = google.get('userinfo')
    email = google_user_info.data['email']

    user = get_user_by_email(email, mongo) 
    if not user:
        user_info = google_user_info.data
        user_info['_id'] = str(ObjectId())  # Convert ObjectId to string
        user_id = mongo.insert_one(user_info).inserted_id
        user_info['_id'] = str(user_id)  # Ensure the user_info has string id
    else:
        user_id = user["_id"]
        user_info = user
        user_info['_id'] = str(user_id)  # Ensure the user_info has string id

    access_token = create_access_token(identity=user_info)
    return redirect(f'{CLIENT_URL}auth/login?token={access_token}', code=302)
