from django.urls import path
from interview.consumers import InterviewConsumer

websocket_urlpatterns = [
    path('ws/interview/<str:interview_id>/', InterviewConsumer.as_asgi()),
]
