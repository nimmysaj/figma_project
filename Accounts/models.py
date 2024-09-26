import re
from django.contrib.auth.models import Permission,Group
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.forms import ValidationError
from django.utils import timezone
import random
from django.core.validators import RegexValidator
import phonenumbers
from figma import settings

# Create your models here.
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
    is_customer = models.BooleanField(default=True)
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
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
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
        return self.email
    
    def __str__(self):
        return self.email if self.email else self.phone_number

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

class Franchise_Type(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=50)

class Franchisee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='franchisee')
    custom_id = models.CharField(max_length=10, unique=True, editable=False, blank=True) 

    about = models.TextField()
    profile_image = models.ImageField(upload_to='f-profile_images/', null=True, blank=True, validators=[validate_file_size])  # Profile image field
    revenue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dealers = models.IntegerField(blank=True, null=True)
    service_providers = models.IntegerField(blank=True, null=True)
    type = models.ForeignKey(Franchise_Type, on_delete=models.CASCADE,related_name='franchisee_type')

    valid_from = models.DateTimeField()
    valid_up_to = models.DateTimeField()
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    verification_id = models.CharField(max_length=255, blank=True, null=True)  
    verificationid_number = models.CharField(max_length=50, blank=True, null=True)  # ID number field
    community_name = models.CharField(max_length=50)


    def save(self, *args, **kwargs):
        if not self.custom_id:
            # Generate the custom ID format
            self.custom_id = f'FR{self.id}'  # Format: FR{id}

        super(Franchisee, self).save(*args, **kwargs)


    def __str__(self):
        return self.custom_id 

    @property
    def franchise_amount(self):
        """Return the amount defined in the Franchise_type."""
        return self.type.amount  


class Dealer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dealer')
    custom_id = models.CharField(max_length=10, unique=True, editable=False, blank=True)  # Custom ID field
    
    about = models.TextField()
    profile_image = models.ImageField(upload_to='d-profile-images/', null=True, blank=True, validators=[validate_file_size])  # Profile image field
    service_providers = models.IntegerField(blank=True, null=True)
    franchisee = models.ForeignKey(Franchisee, on_delete=models.CASCADE)

    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    verification_id = models.CharField(max_length=255, blank=True, null=True)  
    verificationid_number = models.CharField(max_length=50, blank=True, null=True)  # ID number field
    id_copy = models.FileField(upload_to='id-dealer/', blank=True, null=True, validators=[validate_file_size]) 
    
    
    def save(self, *args, **kwargs):
        if not self.custom_id:
            # Generate the custom ID format
            franchisee_id = f'FR{self.franchisee.id}'  # Franchisee ID with prefix FR
            
            # Combine to form the custom ID
            self.custom_id = f'D{self.id}{franchisee_id}'  # Format: D{id}FR{id}

        super(Dealer, self).save(*args, **kwargs)

    def __str__(self):
        return self.custom_id 


class ServiceProvider(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_provider')
    custom_id = models.CharField(max_length=20, unique=True, editable=False, blank=True)  # Custom ID field

    # Service provider-specific fields
    PAYOUT_FREQUENCY_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]
    
    STATUS_CHOICES = [
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PENDING', 'Pending'),
    ]

    
    profile_image = models.ImageField(upload_to='s-profile-images/', null=True, blank=True, validators=[validate_file_size])
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    dealer = models.ForeignKey(Dealer, on_delete=models.PROTECT)
    franchisee = models.ForeignKey(Franchisee, on_delete=models.PROTECT)

    address_proof_document = models.CharField(max_length=255, blank=True, null=True)  
    id_number = models.CharField(max_length=50, blank=True, null=True)  # ID number field
    address_proof_file = models.FileField(upload_to='id-service-pro/', blank=True, null=True, validators=[validate_file_size])  # File upload for address proof
    payout_required = models.CharField(max_length=10, choices=PAYOUT_FREQUENCY_CHOICES)  # Payout frequency field
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    verification_by_dealer= models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    accepted_terms = models.BooleanField(default=False)
    
    
    def save(self, *args, **kwargs):
        if not self.custom_id:
            # Generate the custom ID format
            dealer_id = f'D{self.dealer.id}'  # Dealer ID with prefix D
            franchisee_id = f'FR{self.franchisee.id}'  # Franchisee ID with prefix FR
            
            # Combine to form the custom ID
            self.custom_id = f'SP{self.user.id}{dealer_id}{franchisee_id}'  # Format: SP{id}D{id}FR{id}

        super(ServiceProvider, self).save(*args, **kwargs)



    def __str__(self):
        return self.custom_id

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer')
    custom_id = models.CharField(max_length=20, unique=True, editable=False, blank=True)  # Custom ID field
    
    # Customer-specific fields
    profile_image = models.ImageField(upload_to='c-profile-images/', null=True, blank=True, validators=[validate_file_size])
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])

    def save(self, *args, **kwargs):
        if not self.custom_id:
            # Find the last existing custom ID
            last_custom_id = Customer.objects.order_by('custom_id').last()
            if last_custom_id:
                # Extract the numeric part and increment
                match = re.match(r'USER(\d+)', last_custom_id.custom_id)
                if match:
                    customer_number = int(match.group(1)) + 1
                else:
                    customer_number = 1  # Start from 1 if no previous ID found
            else:
                customer_number = 1  # Start from 1 if no previous ID found

            # Create the custom ID with the USER prefix
            self.custom_id = f'USER{customer_number}'  # No leading zeros

        super(Customer, self).save(*args, **kwargs)

    def __str__(self):
        return self.custom_id

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='otp_received_user')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def generate_otp_code(self):
        """Generate a 4-digit random OTP code."""
        return str(random.randint(1000, 9999))

    def save(self, *args, **kwargs):
        if not self.pk:
            self.otp_code = self.generate_otp_code()
            self.expires_at = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OTP for {self.user.username} - Expires at {self.expires_at}"
