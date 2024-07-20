from django.urls import path
from interview.api import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.getRoutes, name='routes'),   
    path('schedule/', views.scheduleInterview.as_view(), name='schedule'),
    path('schedul/<str:id>', views.updateInterview.as_view(), name='update'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
