from django.urls import path
from . import views

urlpatterns = [
    path('razorpay/payment/', views.Razorpay_Payment, name='Razorpay_Payment'),
    path('razorpay/success/', views.razorpay_success, name='razorpay_success'),
]