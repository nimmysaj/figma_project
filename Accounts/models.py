from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group
from django.core.exceptions import ValidationError
from django.utils import timezone
import random
import string

def validate_file_size(value):
    """Validate the size of the uploaded file."""
    filesize = value.size  # Get the size of the uploaded file
    limit_mb = 5  # Set the file size limit (in MB)

    # Convert MB to bytes and check if the file size exceeds the limit
    if filesize > limit_mb * 1024 * 1024:
        raise ValidationError(f"Maximum file size is {limit_mb}MB")

class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_service_provider = models.BooleanField(default=False)

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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_provider_profile')  # Reference custom user model

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
    address_proof_file = models.FileField(upload_to='address_proofs/', blank=True, null=True, validators=[validate_file_size])  # File upload for address proof
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

class ServiceType(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Collar(models.Model):
    name = models.CharField(max_length=255)
    lead_quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Category(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True, validators=[validate_file_size])
    description = models.TextField()
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])

    def __str__(self):
        return self.title

class Subcategory(models.Model):
    title = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    image = models.ImageField(upload_to='subcategory_images/', null=True, blank=True, validators=[validate_file_size])
    description = models.TextField()
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, related_name='subcategories')
    collar = models.ForeignKey(Collar, on_delete=models.CASCADE, related_name='subcategories')
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])

    def __str__(self):
        return self.title

    def basic_amount(self):
        """Calculate the basic amount based on service type and collar."""
        return self.service_type.amount + self.collar.amount

class ServiceRegister(models.Model):
    service_provider = models.ForeignKey(ServiceProviderProfile, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=50)
    description = models.TextField()
    gstcode = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='service_requests')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='service_requests')
    license = models.FileField(upload_to='service_license/', blank=True, null=True, validators=[validate_file_size])
    image = models.ImageField(upload_to='service_images/', null=True, blank=True, validators=[validate_file_size])
    accepted_terms = models.BooleanField(default=False)

    def __str__(self):
        return self.title
