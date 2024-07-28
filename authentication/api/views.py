from rest_framework.response import Response
from rest_framework.decorators import api_view
from urllib.parse import urlencode
from rest_framework import serializers, status
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from authentication.mixins import PublicApiMixin, ApiErrorsMixin, ApiAuthMixin
from authentication.utils import google_get_access_token, google_get_user_info, generate_tokens_for_user
from authentication.models import User, WatchHistory
from authentication.api.serializers import UserSerializer
from authentication.task import send_welcome_email
from conversation.models import Note, Topic, Video
from conversation.api.serializers import VideoSerializer
from django.core.exceptions import ObjectDoesNotExist

@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/auth/login/google/',
        '/api/auth/refresh/',
        '/api/auth/me/',
        ]    
    return Response(routes)

class WatchHistoryApi(APIView, ApiAuthMixin, ApiErrorsMixin):
    def post(self, request):
        videoId = request.data.get('videoId')
        video_timestamp = request.data.get('video_timestamp', 0)
        if not videoId:
            return Response({'error': 'videoId is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.get(email=request.user.email)
        video = get_object_or_404(Video, videoId=videoId)
        
        try:
            watch_history = WatchHistory.objects.get(username=request.user, video=video)
            watch_history.video_timestamp = video_timestamp
            watch_history.save()
            return Response({'message': 'Watch history updated'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            WatchHistory.objects.create(username=user, video=video, video_timestamp=video_timestamp)
            return Response({'message': 'Watch history created'}, status=status.HTTP_201_CREATED)
        
    def get(self, request):
        user_email = request.user.email
        user = get_object_or_404(User, email=user_email)

        # Fetch user notes and create a dictionary to map videoId to notes
        user_notes = Note.objects.filter(username=user).order_by('-timestamp')
        video_notes_map = {}
        for note in user_notes:
            if note.videoId.videoId not in video_notes_map:
                video_notes_map[note.videoId.videoId] = []
            video_notes_map[note.videoId.videoId].append({
                "notes": note.notes,
                "createdAt": note.timestamp,
            })

        # Fetch user topics and associated videos
        user_topics = Topic.objects.filter(username=user).distinct()
        user_topics_list = []
        for topic in user_topics:
            videos = Video.objects.filter(topic=topic).distinct()
            video_details = []
            for video in videos:
                serializer = VideoSerializer(video)
                video_detail = {
                    "videoId": video.videoId,
                    "description": serializer.data['description'],
                    "addedAt": video.addedAt,
                    "notes": video_notes_map.get(video.videoId, [])
                }
                video_details.append(video_detail)

            user_topics_list.append({
                "topic": {
                    "category": topic.category,
                    "id": topic.category_id,
                },
                "videos": video_details
            })

        return Response({'watch_history': user_topics_list}, status=status.HTTP_200_OK)



class GoogleLoginApi(PublicApiMixin, ApiErrorsMixin, APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get('code')
        error = validated_data.get('error')

        login_url = f'{settings.BASE_FRONTEND_URL}/auth'
    
        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        redirect_uri = f'{settings.BASE_FRONTEND_URL}/auth/loading'
        access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)

        user_data = google_get_user_info(access_token=access_token)

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
                username=f"{first_name} {last_name}",
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

class UserProfileView(APIView):
    def get(self, request):
        user = request.user
        return Response(UserSerializer(user).data)

