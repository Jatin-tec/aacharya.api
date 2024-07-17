from django.urls import path
from authentication.api import views
from django.conf import settings

urlpatterns = [
    path('', views.getRoutes, name='routes'),
    path('login/google/', views.GoogleLoginApi.as_view(), name='login-with-google'),
] 

# add media url to urlpatterns if in debug mode
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)