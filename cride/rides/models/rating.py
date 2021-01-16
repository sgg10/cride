"""Ride Rating Model."""

# Django
from django.db import models

# Utilities
from cride.utils.models import CRideModel

class Rating(CRideModel):
  """Ride rating

    Rates are entities that store the rating a user
    gave to a ride, it range from 1 to 5 and it affects
    the ride offerer's overall reputation.
  """

  ride = models.ForeignKey(
    'rides.Ride', 
    related_name='rated_ride', 
    on_delete=models.CASCADE
  )

  circle = models.ForeignKey('circles.Circle', on_delete=models.CASCADE)

  rating_user = models.ForeignKey(
    'users.User', 
    related_name='rating_user',
    on_delete=models.SET_NULL,
    null=True,
    help_text='User that emits the rating'
  )

  rated_user = models.ForeignKey(
    'users.User', 
    related_name='rated_user',
    on_delete=models.SET_NULL,
    null=True,
    help_text='User that receives the rating.'
  )

  comments =models.TextField(blank=True)

  rating = models.IntegerSmallField(default=1)

  def __str__(self):
    """Return summary."""
    rating_user = self.rating_user.username
    rating = self.rating
    rated_user = self.rated_user.username
    return f'@{rating_user} rated {rating} @{rated_user}'