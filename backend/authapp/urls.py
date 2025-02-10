from django.urls import path, include
from .views import CustomUserViewSet, GoogleOAuth2Login
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', CustomUserViewSet, basename='users')
router.register(r'google', GoogleOAuth2Login, basename='google')

urlpatterns = [
    # path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('', include(router.urls)),
]
