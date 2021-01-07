"""Circle urls."""

# Django
from django.urls import path

# Views
from cride.circles.views import list_circle, create_circle

urlpatterns = [
  path('circles/', list_circle),
  path('circles/create', create_circle),
]