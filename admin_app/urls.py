from django.contrib import admin
from django.urls import path
from admin_app.views import Franchise_TypeView

urlpatterns = [
    path("",Franchise_TypeView.as_view())
]