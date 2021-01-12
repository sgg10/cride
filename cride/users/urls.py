"""Users URLs."""

# Django
from django.urls import path, include

# DRF Simple JWT
from rest_framework.routers import DefaultRouter

# DRF Simple JWT
from rest_framework_simplejwt.views import (
  TokenObtainPairView,
  TokenRefreshView,
)

# Views
from cride.users.views import UserLoginAPIView
from .views import users as user_views

router = DefaultRouter()
router.register(r'users', user_views.UserViewSet, basename='users')

urlpatterns = [
  path('users/login/', UserLoginAPIView.as_view(), name='login'),
  path('users/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  path('', include(router.urls)),
]