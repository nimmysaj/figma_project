from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser,Permission,Group
from django.db import models
from django.utils import timezone
import random
import string

class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_service_provider = models.BooleanField(default=False)

    # Any other fields common to both roles
    phone_number = models.CharField(max_length=15)
    
    groups = models.ManyToManyField(
        Group,
        related_name='app1_user_groups',  # Add a unique related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    # Override user_permissions field with a unique related_name
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='app1_user_permissions'  # Add a unique related_name
    )

    def __str__(self):
        return self.username

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='service_provider_profile')
    
    # Service provider-specific fields
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
    id_number = models.CharField(max_length=50, blank=True, null=True)  # ID number field
    address_proof_file = models.FileField(upload_to='address_proofs/', blank=True, null=True)  # File upload for address proof
    payout_required = models.CharField(max_length=10, choices=PAYOUT_FREQUENCY_CHOICES)  # Payout frequency field

    accepted_terms = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def generate_otp_code(self):
        """Generate a random OTP code."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def save(self, *args, **kwargs):
        if not self.pk:
            self.otp_code = self.generate_otp_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OTP for {self.user.username} - Expires at {self.expires_at}"


