from flask import url_for, redirect, current_app, session
from functools import wraps
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
# jwt
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, JWTManager

def create_user(user, mongo):
    password = user['password']
    hashed_password = generate_password_hash(password)
    user["password"] = hashed_password
    user_id = mongo.insert_one(user).inserted_id
    return user_id

def get_user_by_email(email, mongo):
    return mongo.find_one({"email": email})

def verify_password(user, password):
    return check_password_hash(user['password'], password)

# Decorator for creating auth protected routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'auth_token' not in session:
            return redirect("http://localhost:3000/auth/login", code=302)
        # validate token
        # if not valid, redirect to login
        # if valid, continue
        # get user info
        # pass user info to the function
        user_info = get_user_info()
        return f(user_info, *args, **kwargs)
    return decorated_function

# Get user profile and other info
def get_user_info():
    user_info = session.get('jwt_payload')
    return user_info
