"""Membership permissions."""

# Django REST Framework 
from rest_framework.permissions import BasePermission

# Models
from cride.circles.models import Membership

class IsActiveCircleMember(BasePermission):
  """Allow access only to circle members.

    Excpect that the view implementing this permission
    have a 'circle' attribute assigned.
  """
  
  def has_permission(self, request, view):
    """Verify user is an active member of the circle."""
    try:
      Membership.objects.get(
        user=request.user,
        circle=view.circle,
        is_active=True
      )
    except Membership.DoesNotExist:
      return False
    return True

class IsAdminOrMembershipOwner(BasePermission):
  """
    Allow access only to circle's admin or users
    that are owner of the membership
  """

  def has_permission(self, request, view):
    if view.get_object().user == request.user:
      return True
    try:
      Membership.objects.get(
        circle=view.circle,
        user=request.user,
        is_active=True,
        is_admin=True
      )
    except Membership.DoesNotExist:
      return False
    return True

class IsSelfMember(BasePermission):
  """Allow access only to the owner of the invitations."""

  def has_permission(self, request, view):
    return request.user == view.get_object().user