from django.contrib.auth.models import User,Permission,Group
from django.db import models
from django.utils import timezone
import random
import string

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    
    # Customer-specific fields
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    full_name = models.CharField(max_length=255)
    address = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    house_name = models.CharField(max_length=255, blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    pin_code = models.CharField(max_length=10)
    district = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    def __str__(self):
        return self.full_name