from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=200)
    email = models.EmailField(unique=True, primary_key=True)
    email_verified = models.BooleanField(default=False)
    REGISTRATION_METHODS = [
        ('email', 'Email'),
        ('google', 'Google'),
    ]
    registration_method = models.CharField(max_length=20, default='email', choices=REGISTRATION_METHODS)
    picture_url = models.URLField(null=True, blank=True, max_length=10000)
    picture = models.ImageField(null=True, blank=True, upload_to='profile_pictures')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email