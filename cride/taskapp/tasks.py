"""Celery tasks."""

# Django
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# Celery
from celery.decorators import task, periodic_task
from celery.task.schedules import crontab

# Models
from cride.users.models import User
from cride.rides.models import Ride

# Utilities
import jwt
from datetime import timedelta
import csv

def gen_verification_token(user):
  """Create JWT token that the user can use to verify its account."""
  exp_date = timezone.now() + timedelta(days=3)
  payload = {
    'user': user.username,
    'exp': int(exp_date.timestamp()),
    'type': 'email_confirmation'
  }
  token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
  return token

@task(name='send_confirmation_email', max_retries=3)
def send_confirmation_email(user_pk):
  """Send account verification link to given user."""
  user = User.objects.get(pk=user_pk)
  verification_token = gen_verification_token(user)
  
  subject = f'Welcome @{user.username}! Verify your account to start using Comparte Ride'
  from_email = 'Comparte Ride <noreply@comparteride.com'
  content = render_to_string(
    'emails/users/account_verification.html',
    { 'token': verification_token, 'user': user }
  )
  msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
  msg.attach_alternative(content, 'text/html')
  msg.send()

@periodic_task(name='disable_finish_rides', run_every=crontab(hour=7, minute=30, day_of_week=1))
def disable_finish_rides():
  """Disable finished rides."""
  now = timezone.now()
  offset = now + timedelta(minutes=20)

  # Update rides that have already fisinsh
  rides = Ride.objects.filter(arrival_date__gte=now, arrival_date__lte=offset, is_active=True)
  rides.update(is_active=False)

@periodic_task(name='list_user', run_every=timedelta(seconds=10))
def list_user():
  users = User.objects.all()
  list_user = [['pk', 'username']]
  for user in users:
    list_user.append([user.pk, user.username])
  with open('users.txt', 'w') as file:
    writer = csv.writer(file)
    writer.writerows(list_user)
  print('writing complete')
