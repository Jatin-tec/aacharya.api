
import requests
from typing import Dict, Any
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken

GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'



def generate_tokens_for_user(user):
    """
    Generate access and refresh tokens for the given user
    """
    refresh = RefreshToken.for_user(user)
    print(refresh, 'token_data')
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    return access_token, refresh_token

def google_get_access_token(*, code: str, redirect_uri: str) -> str:
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

    if not response.ok:
        raise ValidationError('Failed to obtain access token from Google.')

    access_token = response.json()['access_token']

    return access_token


def google_get_user_info(*, access_token:  str) -> Dict[str, Any]:
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )                   

    if not response.ok:
        raise ValidationError('Failed to obtain user info from Google.')

    return response.json()


def get_first_matching_attr(obj, *attrs, default=None):
    for attr in attrs:
        if hasattr(obj, attr):
            return getattr(obj, attr)
    return default


def get_error_message(exc) -> str:
    if hasattr(exc, 'message_dict'):
        return exc.message_dict
    error_msg = get_first_matching_attr(exc, 'message', 'messages')

    if isinstance(error_msg, list):
        error_msg = ', '.join(error_msg)

    if error_msg is None:
        error_msg = str(exc)

    return error_msg


def send_email(email, template_name, context, subject):
    # context = {
    #     'name': name,
    #     'email': email,
    #     'site_name': 'https://aacharya.in'
    # }
    # email_subject = 'Welcome to Aacharya!'
    # email_body = render_to_string('email/welcome_email.txt', context)
    email_subject = subject
    email_body_html = render_to_string(template_name, context)
    email_body_text = strip_tags(email_body_html)  # Generate a plain text version of the HTML content
    
    email_message = send_mail(
        subject=email_subject,
        message=email_body_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=email_body_html,
        recipient_list=[email],
        fail_silently=False,
    )
    return email_message
