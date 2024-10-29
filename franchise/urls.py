from django.urls import path
from .views import FranchiseeLoginView,AddServiceView

urlpatterns = [
    path('add-service/', AddServiceView.as_view(), name='add_service'),
    path('login-franchise/', FranchiseeLoginView.as_view(), name='franchise-login'),
]