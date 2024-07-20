from django.urls import path
from conversation.api import views
from django.conf import settings

urlpatterns = [
    path('', views.getRoutes, name='routes'),
    path('transcript/<str:video_id>', views.TranscriptApi.as_view(), name='transcript'),
    path('task/<str:task_id>', views.GetTaskStatus.as_view(), name='task'),
    path('ask/', views.AskApi.as_view(), name='ask'),
] 