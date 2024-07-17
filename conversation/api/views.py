from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from conversation.task import get_video_transcript_task
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
            return Response({'status': 'Success', 'transcript': task_result.result}, status=status.HTTP_200_OK)
        elif task_result.state == 'FAILURE':
            return Response({'status': 'Failed', 'error': str(task_result.result)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'status': task_result.state}, status=status.HTTP_200_OK)
        

class AskApi(ApiAuthMixin, ApiErrorsMixin, APIView):
    def post(self, request):
        # get the user from the request
        email = request.user
        user = User.objects.get(email=email)

        return Response("Ask API endpoint", status=status.HTTP_200_OK)