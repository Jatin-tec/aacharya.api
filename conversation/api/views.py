from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from conversation.task import get_video_transcript_task, generate_response_task, summarize_video
from conversation.api.serializers import TranscriptField, DescriptionField, VideoSerializer
from conversation.models import Video, Conversation, Note

from authentication.mixins import ApiAuthMixin, ApiErrorsMixin
from authentication.models import User

from celery.result import AsyncResult

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


class TranscriptApi(APIView):
    authentication_classes = []
    def get(self, request, video_id):
        print(video_id, 'video_id')
        task = get_video_transcript_task.delay(video_id)
        return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)


class GetTaskStatus(APIView):
    authentication_classes = []
    def get(self, request, task_id):
        task_result = AsyncResult(task_id)
        if task_result.state == 'PENDING':
            return Response({'status': 'Pending'}, status=status.HTTP_200_OK)
        elif task_result.state == 'SUCCESS':
            return Response({'status': 'Success', 'result': task_result.result}, status=status.HTTP_200_OK)
        elif task_result.state == 'FAILURE':
            return Response({'status': 'Failed', 'error': str(task_result.result)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'status': task_result.state}, status=status.HTTP_200_OK)
        

class AskApi(ApiAuthMixin, ApiErrorsMixin, APIView):
    def post(self, request):
        # get the user from the request
        email = request.user.email        
        user_message = request.data.get('message')
        if not user_message:
            return Response({'response': 'message not provided'}, status=status.HTTP_400_BAD_REQUEST)

        timestamp = request.data.get('timestamp', 0)  # Default to 0 if not provided
        video_id = request.query_params.get('q')
        if not video_id:
            return Response({'response': 'video_id not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        task = generate_response_task.delay(user_message=user_message, video_id=video_id, timestamp=timestamp, email=email)
        
        return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
    
class SummarizeApi(ApiAuthMixin, ApiErrorsMixin, APIView):
    def post(self, request):
        video_id = request.query_params.get('q')
        email = request.user.email        
        if not video_id:
            return Response({'response': 'video_id not provided'}, status=status.HTTP_400_BAD_REQUEST)
        conversation = request.data.get('conversation')
        
        task = summarize_video.delay(video_id=video_id, conversation=conversation, email=email)
        
        return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
