from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework import status
from interview.models import Interview
from interview.api.serializers import InterviewSerializer
from authentication.mixins import ApiAuthMixin, ApiErrorsMixin
from interview.tasks import send_interview_schedule_email
from interview.mixins import ApiFormDataMixin
from datetime import datetime
from django.shortcuts import get_object_or_404



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
        if Interview.objects.filter(user=request.user, interview_status__in=['Scheduled', 'Rescheduled']).exists():
            return Response({'error': 'You already have an interview scheduled.'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        data['user'] = request.user
        serializer = InterviewSerializer(data=data)
        if serializer.is_valid():
            interview = serializer.save()
            context = {
                'company_name': interview.company_name,
                'interview_type': interview.interview_type,
                'username': request.user.username,
                'interview_date': datetime.strftime(interview.interview_date, '%Y-%m-%d %H:%M:%S'),
                'interview_code': interview.interview_code,
            }
            send_interview_schedule_email.delay(request.user.email, context, 'Interview Scheduled')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        interviews = Interview.objects.filter(user=request.user)
        if not interviews:
            return Response({'error': 'No interviews found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = InterviewSerializer(interviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class updateInterviewDetailInterview(ApiAuthMixin, ApiErrorsMixin, ApiFormDataMixin, UpdateAPIView):
    def get(self, request, interview_code):
        user_interview = Interview.objects.filter(user=request.user)
        interview = get_object_or_404(user_interview, interview_code=interview_code)
        if not interview:
            return Response({'error': 'Interview not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = InterviewSerializer(interview)
        return Response(serializer.data, status=status.HTTP_200_OK)

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