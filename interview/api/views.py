from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework import status
from interview.models import Interview
from interview.api.serializers import InterviewSerializer
from authentication.mixins import ApiAuthMixin, ApiErrorsMixin
from authentication.models import User
from celery.result import AsyncResult
from interview.mixins import ApiFormDataMixin


@api_view(['GET'])
def getRoutes(request):
    routes = [
        {'GET': '/api/interviews/'},
        {'POST': '/api/interviews/schedule/'},
        {'PUT': '/api/interviews/update/<id>'},
        {'DELETE': '/api/interviews/delete/<id>'},
        ]    
    return Response(routes)

class scheduleInterview(ApiAuthMixin, ApiErrorsMixin, ApiFormDataMixin, CreateAPIView):
    def post(self, request, format=None):
        # not scheduling an interview if user already has an interview of status 'Scheduled' or 'Rescheduled'
        if Interview.objects.filter(user=request.user, interview_status__in=['Scheduled', 'Rescheduled']).exists():
            return Response({'error': 'You already have an interview scheduled.'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        data['user'] = request.user
        serializer = InterviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class updateInterview(ApiAuthMixin, ApiErrorsMixin, ApiFormDataMixin, APIView):
    def put(self, request, id):
        interview = Interview.objects.get(id=id)
        serializer = InterviewSerializer(instance=interview, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        interview = Interview.objects.get(id=id)
        interview.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)