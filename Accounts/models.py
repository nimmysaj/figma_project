from django.db import models

# Create your models here.
class Franchise_Type(models.Model):
    name = models.CharField(max_length=255, unique=True)
    details = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=50)