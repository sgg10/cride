"""Users views."""

# Django REST Framework
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView

# Serializer
from cride.users.serializers import (
  UserLoginSerializer,
  UserModelSerializer,
  UserSignUpSerializer,
  AccountVerificationSerializer
)

class UserLoginAPIView(TokenObtainPairView):
  """User login API view."""
  serializer_class = UserLoginSerializer

class UserViewSet(viewsets.GenericViewSet):
  """User view set.
    Handle sign up, login and account verification
  """
  @action(detail=False, methods=['POST'])
  def signup(self, request):
    """User sing up."""
    serializer = UserSignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    data = UserModelSerializer(user).data
    return Response(data, status=status.HTTP_201_CREATED)

  @action(detail=False, methods=['POST'])
  def verification(self, request):
    """User account verification."""
    serializer = AccountVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    data = { 'message': 'Congratulation, now go to share some rides!' }
    return Response(data, status=status.HTTP_200_OK)
