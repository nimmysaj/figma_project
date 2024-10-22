from django.db import models
# Create your models here.
from django.contrib.auth.models import User

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    dealer = models.ForeignKey(User, related_name='dealer_services', on_delete=models.CASCADE)
    franchise = models.ForeignKey(User, related_name='franchise_services', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Notification(models.Model):
    message = models.CharField(max_length=255)
    recipient = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, related_name='notifications', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.recipient.username} - {self.message}"