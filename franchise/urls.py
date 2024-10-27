from django.urls import include, path
from .views import *




urlpatterns = [
    path('login/', FranchiseeLoginView.as_view(), name='franchise_login'),
    path('service-providers-list/', ServiceProviderListView.as_view(), name='service-providers-list'),
    # path('service-providers/create/', createserviceprovider, name='create-service-provider') # redirects to the create service provider page from the list page
]
 