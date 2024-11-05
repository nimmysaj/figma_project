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
'''
from django.db import models
from PIL import Image
from django.core.exceptions import ValidationError
import uuid

def validate_ad_size(image):
    img = Image.open(image)
    width, height = image.size

    # Define your desired dimensions
    max_width = 800
    max_height = 400 

    if width != max_width or height != max_height:
        raise ValidationError(f"Image dimensions must be {max_width}x{max_height}.")


TARGET_AREA_CHOICES = [
    ('up_to_5_km','Up to 5 km'),
    ('up_to_10_km','Up to 10 km'),
    ('up_to_15_km','Up to 15 km'),
]
AD_TYPE = [
    ('banner','Banner Ad'),
    ('card','Card Ad'),
    ('pop_up','Pop Up Ad'),
]
class Ad_category(models.Model):
    # ad_title = models.CharField(max_length=100)
    type = models.CharField(max_length=50,choices=AD_TYPE)
    description = models.CharField(max_length=200)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    currency = models.CharField(max_length=10,default="INR")
    # ad_image = models.ImageField(upload_to='ad_image/', validators=[validate_ad_size])
    status = models.CharField(max_length=20,choices=[('Active','Active'),('Inactive','Inactive')],default='Active')
    total_views = models.IntegerField(null=True,blank=True)
    total_hits = models.IntegerField(null=True,blank=True)
    image_width = models.IntegerField()
    image_height = models.IntegerField()

class Ad_Management(models.Model):
    ad_id = models.PositiveIntegerField()
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    ad_category = models.ForeignKey(Ad_category,on_delete=models.CASCADE,related_name='ad_category')
    ad_user = model.ForeignKey(User, on_delete=models.CASCADE, related_name='ad_user')
    valid_from = models.DateTimeField()
    valid_up_to = models.DateTimeField()
    target_area = models.CharField(max_length=100,choices=TARGET_AREA_CHOICES, default='up_to_5_km')
    total_days = models.IntegerField()
    total_amount = models.DecimalField(max_digits=5,decimal_places=2)
    image = models.ImageField(upload_to='ad_images/',validators=[])
'''    

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
        ('razorpay','razorpay'),
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
    created_at = models.DateTimeField(auto_now_add=True)
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

class Franchise_Type(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=50,default="INR")

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
            self.custom_id = f'FR{self.user.id}'  # Format: FR{id}

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
            franchisee_id = self.franchisee.custom_id # Franchisee ID with prefix FR
            
            # Combine to form the custom ID
            self.custom_id = f'D{self.user.id}{franchisee_id}'  # Format: D{id}FR{id}

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
    about = models.TextField(null=True,blank=True)

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
            dealer_id = self.dealer.custom_id  # Dealer ID with prefix D
            franchisee_id = self.franchisee.custom_id  # Franchisee ID with prefix FR
            
            # Combine to form the custom ID
            self.custom_id = f'SP{self.user.id}{dealer_id}'  # Format: SP{id}D{id}FR{id}

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
    accepted_terms = models.BooleanField(default=False)

     
    def save(self, *args, **kwargs):
        if not self.custom_id:
            # Combine to form the custom ID
            self.custom_id = f'USER{self.user.id}'  

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
        return f"OTP for {self.user.email or self.user.phone_number} - Expires at {self.expires_at}"
    

class Service_Type(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField()
    #amount = models.DecimalField(max_digits=10, decimal_places=2)
    curreny=models.CharField(max_length=10,null=True,blank=True, default="INR")

    def __str__(self):
        return self.name  
       
class Collar(models.Model):
    name = models.CharField(max_length=255)
    lead_quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    #currency = models.CharField(max_length=50)

    def __str__(self):
        return self.name  
            
class Category(models.Model):
    title = models.CharField(max_length=50,db_index=True)
    image = models.ImageField(upload_to='category-images/', null=True, blank=True, validators=[validate_file_size])  
    description = models.TextField()
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])

    def __str__(self):
        return self.title 

class Subcategory(models.Model):
    title = models.CharField(max_length=50,db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='category')
    image = models.ImageField(upload_to='subcategory-images/', null=True, blank=True, validators=[validate_file_size])  
    description = models.TextField() 
    service_type = models.ForeignKey(Service_Type, on_delete=models.PROTECT,related_name='service_type')
    collar = models.ForeignKey(Collar,on_delete=models.PROTECT,related_name='collar')
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')]) 

    def __str__(self):
        return self.title  

class ServiceRegister(models.Model):
    booking_id=models.UUIDField(default=uuid.uuid4,editable=False,unique=True)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='services')
    description = models.TextField()
    gstcode = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name='serviceregister_category')    
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT,related_name='serviceregister_subcategory') 
    license = models.FileField(upload_to='service-license/', blank=True, null=True, validators=[validate_file_size])
    image = models.ImageField(upload_to='service-images/', null=True, blank=True, validators=[validate_file_size])
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')],default='Inctive')
    accepted_terms = models.BooleanField(default=False)
    available_lead_balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.subcategory.title} by {self.service_provider}"
   
    def update_lead_balance(self, extra_leads=1):
        """
        Update the available lead balance by adding extra leads based on the subcategory's collar.
        Returns the updated lead balance and the amount for the added leads.
        """
        if self.subcategory.service_type.name == "One Time Lead" and self.subcategory.collar:
            # Calculate the amount per lead from the collar model
            lead_quantity = self.subcategory.collar.lead_quantity
            collar_amount = float(self.subcategory.collar.amount)
            
            # Update the available lead balance by adding the specified leads
            self.available_lead_balance += lead_quantity * extra_leads
            self.save()

            # Calculate the total amount to be paid for the added leads
            total_amount = collar_amount * extra_leads
            return self.available_lead_balance, total_amount

        # If not a "One Time Lead", just return the current balance and amount as 0
        return self.available_lead_balance, 0.0
    def basic_amount(self):
        """Calculate the basic amount by combining the subcategory's service type amount and the collar amount."""
        basic_amount = float(self.subcategory.service_type.amount)

        # Add the collar amount if it's present and the subcategory is 'one time lead'
        if self.subcategory.collar and self.subcategory.service_type.title == 'one_time_lead':
            basic_amount += float(self.subcategory.collar.amount)

        return basic_amount

    def save(self, *args, **kwargs):
        """
        Override save method to handle 'Daily Work' services.
        Ensure collar is set to None for 'Daily Work' service type.
        """
        if self.subcategory and self.subcategory.service_type.name == 'Daily Work':
            # No collar is needed for 'Daily Work' service type
            self.available_lead_balance = 0  # You can adjust logic for infinite leads here
        super(ServiceRegister, self).save(*args, **kwargs) 
   
class PaymentRequest(models.Model):
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.PROTECT,related_name='from_paymentrequest')
    dealer = models.ForeignKey(Dealer, on_delete=models.PROTECT,related_name='to_paymentrequest')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    country_code = models.ForeignKey(Country_Codes,max_length=25,on_delete=models.SET_NULL,null=True,blank=True)
    phone = models.CharField(validators=[phone_regex],max_length=15)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    account_holder_name = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=50)
    bank_branch = models.CharField(max_length=50)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=50)
    supporting_documents = models.FileField(upload_to='payment-request/', blank=True, null=True, validators=[validate_file_size])


    def __str__(self):
        return f"Request by {self.service_provider.full_name} to {self.dealer.name} for {self.amount}"


class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    booking_id = models.CharField(max_length=10, unique=True, editable=False)
    title = models.CharField(max_length=20,null=True,blank=True)
    customer = models.ForeignKey(User, on_delete=models.PROTECT,related_name='from_servicerequest')
    service_provider = models.ForeignKey(User, on_delete=models.PROTECT,related_name='to_servicerequest')
    service = models.ForeignKey(ServiceRegister, on_delete=models.CASCADE,related_name='servicerequest')
    work_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    acceptance_status = models.CharField(max_length=20,choices=[('accept', 'accept'), ('decline', 'decline'),('pending', 'pending')],default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    availability_from = models.DateTimeField()  # New field for availability start
    availability_to = models.DateTimeField()    # New field for availability end
    additional_notes = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='service_request/', null=True, blank=True, validators=[validate_file_size])
    reschedule_status = models.BooleanField(default=False)  # New field for rescheduling status


    def __str__(self):
        return f"Request by {self.customer.full_name} for {self.service} ({self.acceptance_status})"

    def clean(self):
        # Ensure the availability_from is before availability_to
        if self.availability_from >= self.availability_to:
            raise ValidationError('Availability "from" time must be before "to" time.')    

class CustomerReview(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    customer = models.ForeignKey(User, on_delete=models.PROTECT,related_name='from_review')  # The customer leaving the review
    service_provider = models.ForeignKey(User, on_delete=models.PROTECT,related_name='to_review')  # The service provider being reviewed
    service_request = models.ForeignKey(ServiceRequest,on_delete=models.SET_NULL,null=True,blank=True,related_name='servicerequest')
    rating = models.IntegerField(choices=RATING_CHOICES)  # Rating from 1 to 5 stars
    image = models.ImageField(upload_to='reviews/', null=True, blank=True, validators=[validate_file_size])
    comment = models.TextField(blank=True, null=True)  # Optional comment
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set the review date

    def __str__(self):
        return f"{self.customer.full_name} - {self.service_provider.full_name} ({self.rating} stars)"
    

class Invoice(models.Model):
    INVOICE_TYPE_CHOICES = [
        ('service_request', 'Service Request'),
        ('dealer_payment', 'Dealer Payment'),
        ('provider_payment', 'Service Provider Payment'),
        ('service_registration','service_registration'),
        ('Ads' ,'Ads'),
        ('lead_purchase','lead_purchase')
    ]
    
    invoice_number = models.PositiveIntegerField(unique=True, editable=False)

    #invoice_type: This field determines whether the invoice is related to a Service Request payment (service_request), a Dealer Payment (dealer_payment), or a Service Provider Payment (provider_payment).
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES)
    
    #A foreign key that links to a ServiceRequest model, which is populated if the payment is related to a customer requesting a service.
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.SET_NULL, null=True, blank=True,related_name='servicerequests_invoices')
    
    #A foreign key that links to a ServiceRequest model, which is populated if the payment is related to a customer requesting a service.
    service_register = models.ForeignKey(ServiceRegister, on_delete=models.SET_NULL, null=True, blank=True,related_name='serviceregister_invoices')

    # Sender (user who is paying) and receiver (user receiving payment)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sent_payment')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='received_payment')
    
    quantity = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    partial_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)  # New field for partial payment
    payment_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid'), ('partially paid', 'partially paid'), ('cancelled', 'Cancelled')], default='pending')

    invoice_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    appointment_date = models.DateTimeField(null=True, blank=True)
    additional_requirements = models.TextField(null=True, blank=True)
    accepted_terms = models.BooleanField(default=False)

    def __str__(self):
        if self.service_request:
            return f"Invoice for Service Request {self.service_request} - {self.payment_status}"
        else:
            return f"Invoice from {self.sender} to {self.receiver} - {self.payment_status}"
        
    def mark_paid(self):
        """Method to mark the invoice as paid."""
        self.payment_status = 'paid'
        self.save()

    def cancel_invoice(self):
        """Method to cancel the invoice."""
        self.payment_status = 'cancelled'
        self.save()

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('invoice_number').last()
            self.invoice_number = last_invoice.invoice_number + 1 if last_invoice else 1
        super().save(*args, **kwargs)    

class Payment(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sent_payments')  # User who sends the payment
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='received_payments')  # User who receives the payment
    transaction_id = models.CharField(max_length=25)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    signature = models.CharField(max_length=256, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES,default='razorpay')
    payment_date = models.DateTimeField(default=timezone.now)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Payment of {self.amount_paid} by {self.sender} to {self.receiver}"

    def mark_completed(self):
        self.payment_status = 'completed'
        self.save()

    def mark_failed(self):
        self.payment_status = 'failed'
        self.save()


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sent_compliant')  
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='received_compliant')  
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')  # Optional link to service request
    subject = models.CharField(max_length=255)
    description = models.TextField()
    images = models.ImageField(upload_to='complaint/', null=True, blank=True, validators=[validate_file_size])
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Complaint by {self.sender} - {self.subject} ({self.status})"
    
    def mark_as_resolved(self, resolution_notes=''):
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.resolution_notes = resolution_notes
        self.save()

    def mark_as_in_progress(self):
        self.status = 'in_progress'
        self.save()

    def reject(self, rejection_reason=''):
        self.status = 'rejected'
        self.resolution_notes = rejection_reason
        self.save()


class DeclineServiceModel(models.Model):
    decline_reason = models.TextField()
    images = models.ImageField(upload_to='decline/', null=True, blank=True, validators=[validate_file_size])
    service_requests = models.ForeignKey(ServiceRequest, on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='decline_services')

    # def __str__(self):
    #     return f"Service of {self.service_requests.customer.full_name} is declined by {self.service_requests.service_provider.full_name}"

    def __str__(self):
        if self.service_requests and self.service_requests.customer:
            return f"Service of {self.service_requests.customer.full_name} is declined by {self.service_requests.service_provider.full_name}"
        return "Service decline request without associated customer."