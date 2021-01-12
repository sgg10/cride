"""Users Serializers."""

# Django
from django.contrib.auth import authenticate, password_validation
from django.core.validators import RegexValidator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

# Django REST Framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Models
from cride.users.models import User, Profile

# Utilities
import jwt
from datetime import timedelta

# Serializers
from cride.users.serializers.profile import ProfileModelSerializer

class UserModelSerializer(serializers.ModelSerializer):
  """User model serializer."""

  profile = ProfileModelSerializer(read_only=True)

  class Meta:
    """Meta class."""
    model = User
    fields = (
      'username',
      'first_name',
      'last_name',
      'email',
      'phone_number',
      'profile'
    )

class UserLoginSerializer(TokenObtainPairSerializer):
  """User login serializer.
    Handle the login request data.
  """

  def validate(self, attrs):
    """Check credentials and get token."""
    user = authenticate(username=attrs['email'], password=attrs['password'])
    if not user:
      raise serializers.ValidationError('Invalid credentials')
    if not user.is_verified:
      raise serializers.ValidationError('Account is not active yet :(')
    refresh = self.get_token(user)
    data = {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
      'user': UserModelSerializer(user).data
    }
    return data

  @classmethod
  def get_token(cls, user):
    """Add custom claim into token"""
    token = super(UserLoginSerializer, cls).get_token(user)
    # token['username'] = user.username
    return token


class UserSignUpSerializer(serializers.Serializer):
  """User Sign up serializer.
    Handle sign up data validation and user/profile creation.
  """
  
  email = serializers.EmailField(
    validators=[UniqueValidator(queryset=User.objects.all())]
  )
  username = serializers.CharField(
    min_length=4,
    max_length=20,
    validators=[UniqueValidator(queryset=User.objects.all())]
  )

  # Phone number
  phone_regex = RegexValidator(
    regex=r'\+?1?\d{1,15}$',
    message='Phone number must be entered in the format: +999999999. Up to 15 digits allowed.'
  )
  phone_number = serializers.CharField(validators=[phone_regex])

  # Password
  password = serializers.CharField(min_length=8)
  password_confirmation = serializers.CharField(min_length=8)

  # Name
  first_name = serializers.CharField(min_length=2, max_length=30)
  last_name = serializers.CharField(min_length=2, max_length=30)

  def validate(self, data):
    """Verify passwords match."""
    passwd = data['password']
    passwd_conf = data['password_confirmation']
    if passwd != passwd_conf:
      raise serializers.ValidationError('Passwords don\'t match.')
    password_validation.validate_password(passwd)
    return data

  def create(self, data):
    """Handle user and profile creation."""
    data.pop('password_confirmation')
    user = User.objects.create_user(**data, is_verified=False, is_client=True)
    Profile.objects.create(user=user)
    self.send_confirmation_email(user)
    return user 

  def send_confirmation_email(self, user):
    """Send account verification link to given user."""
    verification_token = self.gen_verification_token(user)
    
    subject = f'Welcome @{user.username}! Verify your account to start using Comparte Ride'
    from_email = 'Comparte Ride <noreply@comparteride.com'
    content = render_to_string(
      'emails/users/account_verification.html',
      { 'token': verification_token, 'user': user }
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
    msg.attach_alternative(content, 'text/html')
    msg.send()

  def gen_verification_token(self, user):
    """Create JWT token that the user can use to verify its account."""
    exp_date = timezone.now() + timedelta(days=3)
    payload = {
      'user': user.username,
      'exp': int(exp_date.timestamp()),
      'type': 'email_confirmation'
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

class AccountVerificationSerializer(serializers.Serializer):
  """Account verification serializer."""

  token = serializers.CharField()

  def validate_token(self, data):
    """Verify token is valid."""
    try:
      payload = jwt.decode(data, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
      raise serializers.ValidationError('Verification link has expired.')
    except jwt.PyJWTError:
      raise serializers.ValidationError('Invalid token')

    if payload['type'] != 'email_confirmation':
      raise serializers.ValidationError('Invalid token')

    self.context['payload'] = payload
    return data

  def save(self):
    """Update user\'s verified status"""
    payload = self.context['payload']
    user = User.objects.get(username=payload['user'])
    user.is_verified = True
    user.save()