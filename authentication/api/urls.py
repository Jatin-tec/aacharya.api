from django.urls import path
from authentication.api import views
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
urlpatterns = [
    path('', views.getRoutes, name='routes'),
    path('login/google/', views.GoogleLoginApi.as_view(), name='login-with-google'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('me/', views.UserProfileView.as_view(), name='user_profile'),
    path('watch-history/', views.WatchHistoryApi.as_view(), name='watch_history'),
] 

# add media url to urlpatterns if in debug mode
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)