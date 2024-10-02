from django.db import models
import re
import random
import string

# Create your models here.

def validate_file_size(value):
    filesize = value.size
    if filesize > 10485760:  # 10 MB
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    return value

# --------------------------------------------------- A C C O U N T S - M O D E L S .P Y -------------------------------------------------------

# class ServiceProvider(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_provider')
#     custom_id = models.CharField(max_length=20, unique=True, editable=False, blank=True)  # Custom ID field

#     # Service provider-specific fields
#     PAYOUT_FREQUENCY_CHOICES = [
#         ('Daily', 'Daily'),
#         ('Weekly', 'Weekly'),
#         ('Monthly', 'Monthly'),
#     ]
    
#     STATUS_CHOICES = [
#         ('APPROVED', 'Approved'),
#         ('REJECTED', 'Rejected'),
#         ('PENDING', 'Pending'),
#     ]

    
#     profile_image = models.ImageField(upload_to='s-profile-images/', null=True, blank=True, validators=[validate_file_size])
#     date_of_birth = models.DateField(null=True, blank=True)
#     gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

#     dealer = models.ForeignKey(Dealer, on_delete=models.PROTECT)
#     franchisee = models.ForeignKey(Franchisee, on_delete=models.PROTECT)

#     address_proof_document = models.CharField(max_length=255, blank=True, null=True)  
#     id_number = models.CharField(max_length=50, blank=True, null=True)  # ID number field
#     address_proof_file = models.FileField(upload_to='id-service-pro/', blank=True, null=True, validators=[validate_file_size])  # File upload for address proof
#     payout_required = models.CharField(max_length=10, choices=PAYOUT_FREQUENCY_CHOICES)  # Payout frequency field
#     status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
#     verification_by_dealer= models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

#     accepted_terms = models.BooleanField(default=False)
    
    
#     def save(self, *args, **kwargs):
#         if not self.custom_id:
#             # Generate the custom ID format
#             dealer_id = f'D{self.dealer.id}'  # Dealer ID with prefix D
#             franchisee_id = f'FR{self.franchisee.id}'  # Franchisee ID with prefix FR
            
#             # Combine to form the custom ID
#             self.custom_id = f'SP{self.user.id}{dealer_id}{franchisee_id}'  # Format: SP{id}D{id}FR{id}

#         super(ServiceProvider, self).save(*args, **kwargs)



#     def __str__(self):
#         return self.custom_id


################### S E R V I C E - T Y P E

class Service_Type(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField()

    def __str__(self):
        return self.name  

################### C O L L A R

class Collar(models.Model):
    name = models.CharField(max_length=255)
    lead_quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=50)

    def __str__(self):
        return self.name  

################### C A T E G O R I E S

class Category(models.Model):
    title = models.CharField(max_length=50,db_index=True)
    image = models.ImageField(upload_to='category-images/', null=True, blank=True, validators=[validate_file_size])  
    description = models.TextField()
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])

    def __str__(self):
        return self.title 

################### S U B - C A T E G O R I E S

class Subcategory(models.Model):
    title = models.CharField(max_length=50,db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='category')
    image = models.ImageField(upload_to='subcategory-images/', null=True, blank=True, validators=[validate_file_size])  
    description = models.TextField() 
    service_type = models.ForeignKey(Service_Type, on_delete=models.PROTECT,related_name='service_type')
    collar = models.ForeignKey(Collar, on_delete=models.PROTECT,related_name='collar') 
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')]) 

    def __str__(self):
        return self.title  

    def basic_amount(self):
        basic_amount = self.service_type.amount + self.collar.amount
        return basic_amount

# --------------------------------------------------- K E E R T H A N A - M O D E L S .P Y -------------------------------------------------------

class ServiceProvider(models.Model): 
    name = models.CharField(max_length=100)
    subcategory = models.ForeignKey(Subcategory, related_name='service_providers', on_delete=models.CASCADE)
    description = models.TextField()
    contact_info = models.CharField(max_length=255)

    def __str__(self):
        return self.name
