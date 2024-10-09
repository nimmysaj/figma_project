from django.db import models
from customer.models import Customer

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='icons/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='category')
    icon = models.ImageField(upload_to='icons/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])

    def __str__(self):
        return self.name

class ServiceProvider(models.Model):
    name = models.CharField(max_length=100)
    subcategory = models.ForeignKey(Subcategory, related_name='service_providers', on_delete=models.CASCADE)
    description = models.TextField()
    contact_info = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])

    def __str__(self):
        return self.name

class Complaint(models.Model):
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='complaints')
    custom_id = models.CharField(max_length=20, editable=False, blank=True)  # Store custom_id from Customer
    title = models.CharField(max_length=255)
    description = models.TextField()
    additional_requirements = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Resolved', 'Resolved')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    images = models.ImageField(upload_to='complaint_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.custom_id:  # Only set if custom_id is not already set
            self.custom_id = self.customer.custom_id  # Set from linked customer
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
