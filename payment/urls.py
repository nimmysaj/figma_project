from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    
    
    path('create_payment_view/', create_payment_view, name='create_payment_view'),
    path('create_payment_post/', create_payment_post, name='create_payment_post'),
    path('verify_payment/', verify_payment, name='verify_payment'),  # Add verify payment URL
    path('payment_success/<int:payment_id>/',payment_success, name='payment_success'),
    path('payment_success_post/',payment_success_post, name='payment_success_post'),
    # path('payment_receipt/<str:transaction_id>/',payment_receipt, name='payment_receipt'),

]