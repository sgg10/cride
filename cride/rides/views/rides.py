"""Rides views."""

# Django REST Framework
from rest_framework import mixins, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

# Models
from cride.circles.models import Circle

# Serializers
from cride.rides.serializers import (
  CreateRideSerializer, 
  RideModelSerializer,
  JoinSerializer,
  EndRideSerializer,
  CreateRideRatingSerializer
)

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.memberships import IsActiveCircleMember
from cride.rides.permissions.rides import IsRideOwner, IsNotRideOwner

# Filters
from rest_framework.filters import SearchFilter, OrderingFilter

# Utilities
from datetime import timedelta
from django.utils import timezone 

class RideViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):

  filter_backends = (SearchFilter, OrderingFilter)
  DEFAULT_ORDERING = ('departure_date', 'arrival_date', 'available_seats')
  ordering = DEFAULT_ORDERING
  orderin_fields = DEFAULT_ORDERING
  search_fields = ('departure_location', 'arrival_location')

  def dispatch(self, request, *args, **kwargs):
    """."""
    slug_name = kwargs['slug_name']
    self.circle = get_object_or_404(Circle, slug_name=slug_name)
    return super(RideViewSet, self).dispatch(request, *args, **kwargs)

  def get_permissions(self):
    """Assing permission based on action."""
    permission = [IsAuthenticated, IsActiveCircleMember]
    if self.action in ['update', 'partial_update', 'finish']:
      permission.append(IsRideOwner)
    if self.action == 'join':
      permission.append(IsNotRideOwner)
    return [p() for p in permission]

  def get_serializer_context(self):
    """Add circle to serializer context."""
    context = super(RideViewSet, self).get_serializer_context()
    context['circle'] = self.circle
    return context

  def get_serializer_class(self):
    """Return serializer based on action."""
    if self.action == 'create':
      return CreateRideSerializer
    if self.action == 'join':
      return JoinSerializer
    if self.action == 'finish':
      return EndRideSerializer
    if self.action == 'rate':
      return CreateRideRatingSerializer
    return RideModelSerializer

  def get_queryset(self):
    """Return active circle's rides."""
    if self.action not in ['finish', 'retrieve']:
      offset = timezone.now() + timedelta(minutes=10)
      return self.circle.ride_set.filter(
        departure_date__gte=offset,
        is_active=1,
        available_seats__gte=1
      )
    return self.circle.ride_set.all()
  
  @action(detail=True, methods=['POST'])
  def join(self, request, *args, **kwargs):
    """Add requesting user to ride."""
    ride = self.get_object()
    serializer_class = self.get_serializer_class()
    serializer = serializer_class(
      ride,
      data={ 'passenger': str(request.user) },
      context={ 'ride': ride, 'circle': self.circle },
      partial=True
    ) 
    serializer.is_valid(raise_exception=True)
    ride = serializer.save()
    data = RideModelSerializer(ride).data
    return Response(data, status=status.HTTP_200_OK)

  @action(detail=True, methods=['POST'])
  def finish(self, request, *args, **kwargs):
    """Call by owners to finish a ride"""
    ride = self.get_object()
    serializer_class = self.get_serializer_class()
    serializer = serializer_class(
      ride,
      data={ 'is_active': False, 'current_time': timezone.now() },
      context=self.get_serializer_context(),
      partial=True
    ) 
    serializer.is_valid(raise_exception=True)
    ride = serializer.save()
    data = RideModelSerializer(ride).data
    return Response(data, status=status.HTTP_200_OK)

  @action(detail=True, methods=['POST'])
  def rate(self, request, *args, **kwargs):
    """Rate ride."""
    ride = self.get_object()
    serializer_class = self.get_serializer_class()
    context = self.get_serializer_context()
    context['ride'] = ride
    serializer = serializer_class(
      data=request.data,
      context=context
    )
    serializer.is_valid(raise_exception=True)
    ride = serializer.save()
    data = RideModelSerializer(ride).data
    return Response(data, status=status.HTTP_201_CREATE)
