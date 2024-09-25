# from django.contrib.auth.models import User,Permission,Group
from django.db import models
from django.utils import timezone
import random
import string

class CustomerProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    address = models.TextField()
    house_name = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    district = models.CharField(max_length=50)
    state = models.CharField(max_length=50)

    def __str__(self):
        return self.full_name
