from flask import url_for, redirect, current_app, session
from functools import wraps
from flask import request

# Decorator for creating auth protected routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'jwt_payload' not in session:
            return redirect("/auth/login")
        return f(*args, **kwargs)
    return decorated_function

# Get user profile and other info
def get_user_info():
    user_info = session.get('jwt_payload')
    return user_info
