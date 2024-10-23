from django.db import models

# Create your models here.
class ServiceProvider(models.Model):
    id = models.AutoField(primary_key=True)
    franchise_id = models.IntegerField()
    name = models.CharField(max_length=255)
    phno = models.CharField(max_length=20)
    email = models.EmailField()
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    rating = models.DecimalField(max_digits=5, decimal_places=2)
    dealer_id = models.IntegerField()

    def __str__(self):
        return self.name