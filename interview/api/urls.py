from django.urls import path
from interview.api import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.getRoutes, name='routes'),   
    path('schedule/', views.scheduleInterview.as_view(), name='schedule'),
    path('detail/<str:interview_code>/', views.updateInterviewDetailInterview.as_view(), name='interview'),
    path('schedule/<str:interview_code>/', views.updateInterviewDetailInterview.as_view(), name='update'),
    path('reschedule/<str:interview_code>/', views.updateInterviewDetailInterview.as_view(), name='reschedule'),
    path('delete/<str:interview_code>/', views.updateInterviewDetailInterview.as_view(), name='delete'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
