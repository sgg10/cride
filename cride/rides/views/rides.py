"""Rides views."""

# Django REST Framework
from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404

# Models
from cride.circles.models import Circle

# Serializers
from cride.rides.serializers import CreateRideSerializer

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import IsActiveCircleMember

class RideViewSet(mixins.CreateModelMixin,
                  viewsets.GenericViewSet):

  serializer_class = CreateRideSerializer
  permission_clasess = [IsAuthenticated, IsActiveCircleMember]

  def dispatch(self, request, *args, **kwargs):
    """."""
    slug_name = kwargs['slug_name']
    self.circle = get_object_or_404(Circle, slug_name=slug_name)
    return super(RideViewSet, self).dispatch(request, *args, **kwargs)