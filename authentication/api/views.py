from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from urllib.parse import urlencode
from rest_framework import serializers
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.response import Response
from authentication.mixins import PublicApiMixin, ApiErrorsMixin

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from authentication.mixins import PublicApiMixin, ApiErrorsMixin
from authentication.utils import google_get_access_token, google_get_user_info, generate_tokens_for_user
from authentication.models import User
from authentication.api.serializers import UserSerializer

from authentication.task import send_welcome_email

def generate_tokens_for_user(user):
    """
    Generate access and refresh tokens for the given user
    """
    serializer = TokenObtainPairSerializer()
    token_data = serializer.get_token(user)
    access_token = token_data.access_token
    refresh_token = token_data
    return access_token, refresh_token


class GoogleLoginApi(PublicApiMixin, ApiErrorsMixin, APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        print(input_serializer, 'input_serializer')
        print(input_serializer.is_valid(), 'input_serializer.is_valid()')
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get('code')
        error = validated_data.get('error')

        login_url = f'{settings.BASE_FRONTEND_URL}/auth'
    
        if error or not code:
            print('error', error)
            print('code', code)
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        redirect_uri = f'{settings.BASE_FRONTEND_URL}/auth/loading'
        print(redirect_uri, 'redirect_uri')
        access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)

        user_data = google_get_user_info(access_token=access_token)

        print(user_data, 'user_data')

        try:
            user = User.objects.get(email=user_data['email'])
            access_token, refresh_token = generate_tokens_for_user(user)
            response_data = {
                'user': UserSerializer(user).data,
                'access_token': str(access_token),
                'refresh_token': str(refresh_token)
            }
            return Response(response_data)
        except User.DoesNotExist:
            first_name = user_data.get('given_name', '')
            last_name = user_data.get('family_name', '')
            email = user_data['email']
            email_verified = user_data.get('email_verified', False)
            picture_url = user_data.get('picture', None)

            user = User.objects.create(
                username=f"f{first_name} {last_name}",
                email=email,
                email_verified=email_verified,
                first_name=first_name,
                last_name=last_name,
                picture_url=picture_url,
                registration_method='google',
            )
         
            access_token, refresh_token = generate_tokens_for_user(user)
            response_data = {
                'user': UserSerializer(user).data,
                'access_token': str(access_token),
                'refresh_token': str(refresh_token)
            }
            send_welcome_email.delay(first_name, email)
            return Response(response_data)

@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token/',
        '/api/token/refresh/',
        '/api/token/verify/',

        '/api/auth/register/',
        '/api/auth/login/',
        '/api/auth/logout/',
        
        '/api/auth/users/',
        '/api/auth/user/<str:pk>/',
        '/api/auth/user/<str:pk>/update/',
        '/api/auth/user/<str:pk>/delete/',
        ]    
    return Response(routes)
