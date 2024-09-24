from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group
from django.utils import timezone
import random
import string

class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_service_provider = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    # Any other fields common to both roles
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Allow blank/nullable phone number

    groups = models.ManyToManyField(
        Group,
        related_name='app1_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='app1_user_permissions',
    )

    def __str__(self):
        return self.username
    


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    full_name = models.CharField(max_length=255)
    address = models.TextField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    house_name = models.CharField(max_length=255, blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    pin_code = models.CharField(max_length=10)
    district = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    def __str__(self):
        return self.full_name


class ServiceProviderProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_provider_profile')  # Reference custom user model
                                
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    PAYOUT_FREQUENCY_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]

    full_name = models.CharField(max_length=255)
    address = models.TextField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    house_name = models.CharField(max_length=255, blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    pin_code = models.CharField(max_length=10)
    district = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    address_proof_document = models.CharField(max_length=255, blank=True, null=True)  
    id_number = models.CharField(max_length=50, blank=True, null=True)
    address_proof_file = models.FileField(upload_to='address_proofs/', blank=True, null=True)
    payout_required = models.CharField(max_length=10, choices=PAYOUT_FREQUENCY_CHOICES)

    accepted_terms = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class OTP(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Reference custom user model
    otp_code = models.CharField(max_length=6, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()


    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def generate_otp_code(self):
        return str(random.randint(1000,9999))
    
    def save(self,*args, **kwargs):
        if not self.pk:
            self.otp_code=self.generate_otp_code()
            self.expires_at=timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Otp for {self.user.username}- Expires at {self.expires_at}"