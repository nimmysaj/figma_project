from django.urls import path
from .views import UserCreateView,CustomerListView


urlpatterns = [
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('usersview/', CustomerListView.as_view(), name='customer-list')

]