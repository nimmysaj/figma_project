from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Service, Notification

@receiver(post_save, sender=Service)
def notify_dealer_and_franchise(sender, instance, created, **kwargs):
    # Notification message
    if created:
        message = f"New service '{instance.name}' has been registered."
    else:
        message = f"Service '{instance.name}' has been updated."

    # Notify the dealer
    Notification.objects.create(
        message=message,
        recipient=instance.dealer,
        service=instance
    )

    # Notify the franchise
    Notification.objects.create(
        message=message,
        recipient=instance.franchise,
        service=instance
    )