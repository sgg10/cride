"""Users views."""

# Django REST Framework
from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView

# Permissions
from rest_framework.permissions import (
  AllowAny,
  IsAuthenticated
)
from cride.users.permissions import IsAccountOwner

# Serializer
from cride.users.serializers import (
  UserLoginSerializer,
  UserModelSerializer,
  UserSignUpSerializer,
  AccountVerificationSerializer,
  ProfileModelSerializer
)
from cride.circles.serializers import CircleModelSerializer

# Models
from cride.users.models import User
from cride.circles.models import Circle

class UserLoginAPIView(TokenObtainPairView):
  """User login API view."""
  serializer_class = UserLoginSerializer

class UserViewSet(mixins.RetrieveModelMixin, 
                  mixins.UpdateModelMixin, 
                  viewsets.GenericViewSet):
  """User view set.
    Handle sign up, login and account verification
  """

  queryset = User.objects.filter(is_active=True, is_client=True)
  serializer_class = UserModelSerializer
  lookup_field = 'username'

  def get_permissions(self):
    """Assing permissions based on action."""
    if self.action in ['signup', 'login', 'verify']:
      permissions = [AllowAny]
    elif self.action in ['retrieve', 'update', 'partial_update', 'profile']:
      permissions = [IsAuthenticated, IsAccountOwner]
    else:
      permissions = [IsAuthenticated]
    return [permission() for permission in permissions]

  @action(detail=False, methods=['POST'])
  def signup(self, request):
    """User sing up."""
    serializer = UserSignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    data = UserModelSerializer(user).data
    return Response(data, status=status.HTTP_201_CREATED)

  @action(detail=False, methods=['POST'])
  def verify(self, request):
    """User account verification."""
    serializer = AccountVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    data = { 'message': 'Congratulation, now go to share some rides!' }
    return Response(data, status=status.HTTP_200_OK)

  @action(detail=True, methods=['PUT', 'PATCH'])
  def profile(self, request, *args, **kwargs):
    """Update Profile data."""
    user = self.get_object()
    profile = user.profile
    partial = request.method == 'PATCH'
    serializer = ProfileModelSerializer(
      profile,
      data=request.data,
      partial=partial
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    data = UserModelSerializer(user).data
    return Response(data)

  def retrieve(self, request, *args, **kwargs):
    """Add extra data to the response."""
    response = super(UserViewSet, self).retrieve(request, *args, **kwargs)
    circles = Circle.objects.filter(
      members=request.user,
      membership__is_active=True
    )
    data = {
      'user': response.data,
      'circles': CircleModelSerializer(circles, many=True).data
    }
    response.data = data
    return response