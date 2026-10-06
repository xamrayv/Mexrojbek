from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
"""
email
first_name
"""

class User(AbstractUser):
    profile = models.URLField(blank=True, null=True)
    bio = models.TextField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.username