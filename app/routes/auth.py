from flask import Blueprint, redirect, url_for, session, current_app, session
from urllib.parse import urlencode
import os, binascii
import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login')
def login_route():
    oauth = current_app.oauth
    # Generate a nonce and save it in the session
    nonce = binascii.hexlify(os.urandom(16)).decode()
    session['nonce'] = nonce
    return oauth.auth0.authorize_redirect(redirect_uri=current_app.config['AUTH0_CALLBACK_URL'], nonce=nonce)

@bp.route('/callback')
def callback():
    oauth = current_app.oauth
    # Retrieve the nonce from the session
    nonce = session.get('nonce')
    # The nonce is a required argument for parse_id_token for validation
    token = oauth.auth0.authorize_access_token()
    user = oauth.auth0.parse_id_token(token, nonce=nonce)
    session['jwt_payload'] = user
    # It's a good practice to remove the nonce from the session after it's used
    session.pop('nonce', None)

    db = current_app.db["users"]

    print(user, "user here")

    # create or update user
    user = db.find_one({"sub": session['jwt_payload']["sub"]})

    if user is None:
        user = {
            "sub": session['jwt_payload']["sub"],
            "email": session['jwt_payload']["email"],
            "name": session['jwt_payload']["name"],
            "picture": session['jwt_payload']["picture"],
            "created_at": datetime.datetime.now(),
            "last_login": datetime.datetime.now()
        }
        db.insert_one(user)
    else:
        user.update({
            "last_login": datetime.datetime.now()
        })

    return redirect('/dashboard')

@bp.route('/logout')
def logout():
    session.clear()
    oauth = current_app.oauth
    params = {'returnTo': url_for('home', _external=True), 'client_id': current_app.config['AUTH0_CLIENT_ID']}
    return redirect(oauth.auth0.api_base_url + '/v2/logout?' + urlencode(params))
