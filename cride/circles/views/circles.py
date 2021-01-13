"""Circle views."""

# Django REST Framework
from rest_framework import viewsets, mixins
from rest_framework.exceptions import MethodNotAllowed

# Models
from cride.circles.models import Circle, Membership

# Serializers
from cride.circles.serializers import CircleModelSerializer

# Permissions
from cride.circles.permissions.circles import IsCircleAdmin
from rest_framework.permissions import IsAuthenticated

# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

class CircleViewSet(viewsets.ModelViewSet):
  """Circle view set."""
  
  serializer_class = CircleModelSerializer
  lookup_field = 'slug_name'

  # Filters
  filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
  search_fields = ('slug_name', 'name')
  ordering_fields = ('rides_offered', 'rides_taken', 'name', 'create')
  ordering = ('-members__count', '-rides_offered', '-rides_taken')
  filter_fields = ('verified', 'is_limited')

  def get_permissions(self):
    """Asing permissions based on action."""
    permissions = [IsAuthenticated]
    if self.action in ['update', 'partial_update']:
      permissions.append(IsCircleAdmin)
    return [permission() for permission in permissions]

  def destroy(self, request, pk=None):
    """Deny DELETE method."""
    raise MethodNotAllowed('DELETE')

  def get_queryset(self):
    """Restrict list to public-only."""
    queryset = Circle.objects.all()
    if self.action == 'list':
      return queryset.filter(is_public=True)
    return queryset

  def perform_create(self, serializer):
    """Assign circle admin."""
    circle = serializer.save()
    user = self.request.user
    profile = user.profile
    Membership.objects.create(
      user=user,
      profile=profile,
      circle=circle,
      is_admin=True,
      remaining_invitations=10
    )
