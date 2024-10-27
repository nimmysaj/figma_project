from django.urls import path
from . import views

urlpatterns = [
    path('add-service/', views.add_service, name='add_service'),
]
