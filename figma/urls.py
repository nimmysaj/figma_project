from django.contrib import admin
from django.urls import path, include  # Include this for app URLs

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('Accounts.urls')),  # Include the URLs from the Accounts app
]
