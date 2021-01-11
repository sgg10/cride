"""Users views."""

# Django REST Framework
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

# Serializer
from cride.users.serializers import (
  UserLoginSerializer,
  UserModelSerializer,
  UserSignUpSerializer,
  AccountVerificationSerializer
)

class UserLoginAPIView(APIView):
  """User login API view."""

  def post(self, request, *args, **kwargs):
    """Handle HTTP POST request."""
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user, token = serializer.save()
    data = {
      'user': UserModelSerializer(user).data,
      'access_token': token
    }
    return Response(data, status=status.HTTP_201_CREATED)

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
