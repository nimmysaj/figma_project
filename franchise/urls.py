from django.urls import path
from .views import FranchiseeLoginView


urlpatterns = [
    path('login/', FranchiseeLoginView.as_view(), name='franchise_login'),

]
