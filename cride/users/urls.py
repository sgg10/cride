"""Users URLs."""

# Django
from django.urls import path

# DRF Simple JWT
from rest_framework_simplejwt.views import (
  TokenObtainPairView,
  TokenRefreshView,
)

# Views
from cride.users.views import (
  UserLoginAPIView,
  UserSignUpAPIView,
  AccountVerificationAPIView
)

urlpatterns = [
  path('users/login/', UserLoginAPIView.as_view(), name='login'),
  path('users/signup/', UserSignUpAPIView.as_view(), name='signup'),
  path('users/verify/', AccountVerificationAPIView.as_view(), name='verify'),
  path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
  path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]