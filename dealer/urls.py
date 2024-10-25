from django.urls import include, path
from service_provider.views import ResetPasswordView
from rest_framework.routers import DefaultRouter
from .views import *


urlpatterns = [

    path('login/', DealerLoginView.as_view(), name='dealer_login'),
    path('service-providers/', DealerServiceProviderListView.as_view(), name='dealer-service-providers'),
    path('search/', SearchAPIView.as_view(), name='search'),
]