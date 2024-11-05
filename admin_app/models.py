from django.db import models
from django.db import models
from PIL import Image
from django.core.exceptions import ValidationError
import uuid
from Accounts.models import *

def validate_ad_size(image):
    img = Image.open(image)
    width, height = image.size

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
    ad_type = models.CharField(max_length=50,choices=AD_TYPE)
    description = models.CharField(max_length=200)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    currency = models.CharField(max_length=10,default="INR")
    status = models.CharField(max_length=20,choices=[('Active','Active'),('Inactive','Inactive')],default='Active')
    total_views = models.IntegerField(null=True,blank=True)
    total_hits = models.IntegerField(null=True,blank=True)
    image_width = models.IntegerField()
    image_height = models.IntegerField()
    def __str__(self):
        return self.ad_type

class Ad_Management(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    ad_category = models.ForeignKey(Ad_category,on_delete=models.CASCADE,related_name='ad_category')
    valid_from = models.DateTimeField()
    valid_up_to = models.DateTimeField()
    target_area = models.CharField(max_length=100,choices=TARGET_AREA_CHOICES, default='up_to_5_km')
    total_days = models.IntegerField(default=0,null=True)
    total_amount = models.DecimalField(max_digits=5,decimal_places=2,default=0.00,null=True)
    image = models.ImageField(upload_to='ad_images/',validators=[])
    ad_user = models.ForeignKey(User,on_delete=models.PROTECT,related_name='ad_user')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('in progress', 'In Progress'), ('cancelled', 'Cancelled')], default='pending')

# class Payout_Schedule(models.Model):
#     user_type = models.CharField(max_length=20, choices=[('franchisee', 'Franchisee'),('dealer', 'Dealer'),('service provider', 'Service Provider'),('customer', 'Customer'), ('others', 'Others')], default='service provider')
#     user_id = models.ForeignKey(User,on_delete=models.PROTECT,related_name='user_id')
#     auto_payout = models.CharField(max_length=20, choices=[('daily', 'Daily'),('weekly', 'Weekly'),('monthly', 'Monthly')], default='monthly')
#     manual_payout = models.DateTimeField()
#     payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
#     account_holder_name = models.CharField(max_length=50)
#     bank_branch = models.CharField(max_length=50)
