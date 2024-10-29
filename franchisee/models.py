# from django.db import models
# from Accounts.models import ServiceProvider,Category,Subcategory
# import uuid
# from django.forms import ValidationError

# def validate_file_size(value):
#     filesize = value.size
#     if filesize > 10485760:  # 10 MB
#         raise ValidationError("The maximum file size that can be uploaded is 10MB")
#     return value


# class AddNewService(models.Model):
    
#     STATUS_CHOICES = [
#         ('Draft', 'Draft'),
#         ('Submitted', 'Submitted'),
#         ('Deleted', 'Deleted')
#     ]
#     id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
#     service_name = models.CharField(max_length=50)
#     service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='services')
#     description = models.TextField()
#     gstcode = models.CharField(max_length=50)
#     category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name='serviceregister_category')    
#     subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT,related_name='serviceregister_subcategory') 
#     license = models.FileField(upload_to='service-license/', blank=True, null=True, validators=[validate_file_size])
#     image = models.ImageField(upload_to='service-images/', null=True, blank=True, validators=[validate_file_size])
#     status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')],default='Active')
#     accepted_terms = models.BooleanField(default=False)
#     available_lead_balance = models.IntegerField(default=0)

#     def __str__(self):
#         return f"{self.subcategory.title} by {self.service_provider}"