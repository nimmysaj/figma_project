# from django.contrib.auth.models import User,Permission,Group
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import re
import random
import string
# from Accounts.validators import validate_file_size  

def validate_file_size(value):
    filesize = value.size
    if filesize > 10485760:  # 10 MB
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    return value

class Customer(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer')
    custom_id = models.CharField(max_length=20, unique=True, editable=False, blank=True)  # Custom ID field
    profile_image = models.ImageField(upload_to='c-profile-images/', null=True, blank=True, validators=[validate_file_size])#Customer specific field
    full_name = models.CharField(max_length=100)
    address = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)#Customer specific field
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)#Customer specific field
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])#Customer specific field
    house_name = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    district = models.CharField(max_length=50)
    state = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        if not self.custom_id:
            # Generate a custom ID if it doesn't exist
            last_custom_id = Customer.objects.order_by('custom_id').last()
            if last_custom_id:
                match = re.match(r'USER(\d+)', last_custom_id.custom_id)
                if match:
                    customer_number = int(match.group(1)) + 1
                else:
                    customer_number = 1
            else:
                customer_number = 1
            self.custom_id = f'USER{customer_number}'

        # Ensure that super save is called with all arguments
        super(Customer, self).save(*args, **kwargs)

    def _str_(self):
        return self.custom_id