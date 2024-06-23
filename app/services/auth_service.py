from flask import url_for, redirect, current_app, session
from functools import wraps
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(email, password, mongo):
    hashed_password = generate_password_hash(password)
    user_id = mongo.insert_one({
        "email": email,
        "password": hashed_password
    }).inserted_id
    return user_id

def get_user_by_email(email, mongo):
    return mongo.find_one({"email": email})

def verify_password(user, password):
    return check_password_hash(user['password'], password)

# Decorator for creating auth protected routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect("http://localhost:3000/auth/login", code=302)
        return f(*args, **kwargs)
    return decorated_function

# Get user profile and other info
def get_user_info():
    user_info = session.get('jwt_payload')
    return user_info
