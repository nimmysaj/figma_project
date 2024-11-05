from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path('payment/', PaymentPageView.as_view(), name='payment_page'),  # URL for payment page
    # path('generate_signature/',PaymentTestView.as_view(),name='generate_signature'),

]