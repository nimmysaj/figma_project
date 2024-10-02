from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Customer

@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:  # Check if the user is not a superuser
        Customer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    if not instance.is_superuser:
        customer = Customer.objects.filter(user=instance).first()  # Get customer if exists
        if customer:  # Only save if customer profile exists
            customer.save()
