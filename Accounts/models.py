import re
from django.contrib.auth.models import Permission,Group
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.forms import ValidationError
from django.utils import timezone
import random
from django.core.validators import RegexValidator
import phonenumbers
from django.conf import settings
import uuid

phone_regex = RegexValidator(
        regex=r'^\d{9,15}$', 
        message="Phone number must be between 9 and 15 digits."
    )

def validate_file_size(value):
    filesize = value.size
    if filesize > 10485760:  # 10 MB
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    return value

class Country_Codes(models.Model):
    country_name = models.CharField(max_length=100,unique=True)
    calling_code = models.CharField(max_length=10,unique=True)

    def __str__(self):
        return f"{self.country_name} ({self.calling_code})"
    
    class Meta:
        ordering = ['calling_code']

class State(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash'),
    ]



class UserManager(BaseUserManager):
    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        if not email and not phone_number:
            raise ValueError('Either email or phone number must be provided')

        # Normalize the email if provided
        if email:
            email = self.normalize_email(email)

        # Handle phone number validation if provided and not a superuser
        if phone_number and not extra_fields.get('is_superuser'):
            full_number = f"{extra_fields.get('country_code')}{phone_number}"
            try:
                parsed_number = phonenumbers.parse(full_number, None)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise ValidationError("Invalid phone number.")
                phone_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            except phonenumbers.NumberParseException:
                raise ValidationError("Invalid phone number format.")

        # Create and return the user object
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if email is None:
            raise ValueError('Superuser must have an email address.')

        return self.create_user(email=email, phone_number=phone_number, password=password, **extra_fields)


class User(AbstractBaseUser):
    # Role-based fields
    is_customer = models.BooleanField(default=False)
    is_service_provider = models.BooleanField(default=False)
    is_franchisee = models.BooleanField(default=False)
    is_dealer = models.BooleanField(default=False)
    
    # Admin-related fields
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    # Any other fields common to both roles
    full_name = models.CharField(max_length=255)
    address = models.CharField(max_length=30)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    pin_code = models.CharField(max_length=10)
    district = models.ForeignKey('District', on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey('State', on_delete=models.SET_NULL, null=True, blank=True)

    watsapp = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True,validators=[phone_regex], null=True, blank=True)
    country_code = models.ForeignKey('Country_Codes', on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []

    objects = UserManager()
    
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
        return self.email if self.email else self.phone_number

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

class Invoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
    ]
    INVOICE_TYPE_CHOICES = [
        ('service_request', 'Service Request'),
        ('dealer_payment', 'Dealer Payment'),
        ('provider_payment', 'Service Provider Payment'),
        ('Ads' ,'Ads')
    ]
    PAYMENT_TYPE_CHOICES = [
        ('partial', 'Partial Payment'),
        ('full', 'Full Payment'),
    ]

    
    invoice_number = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paying = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES)
    payment_type = models.CharField(
        max_length=20, choices=PAYMENT_TYPE_CHOICES, default='full'
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending'
    )
    invoice_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    sender = models.ForeignKey(User, related_name='invoices_sent', on_delete=models.PROTECT, null=True, blank=True)
    receiver = models.ForeignKey(User, related_name='invoices_received', on_delete=models.PROTECT, null=True, blank=True)
    appointment_date = models.DateTimeField()
    accepted_terms = models.BooleanField(default=False)
    additional_requirements = models.TextField(null=True, blank=True)
    order_id = models.CharField(max_length=100, null=True, blank=True)  

    def __str__(self):
        return f"Invoice for {self.invoice_number} - {self.payment_status}"


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    signature = models.CharField(max_length=250, null=True, blank=True)
    order_id = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    sender = models.ForeignKey(User, related_name='sent_payments', on_delete=models.PROTECT, null=True, blank=True)
    receiver = models.ForeignKey(User, related_name='received_payments', on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Invoice number -{self.invoice.invoice_number}"
