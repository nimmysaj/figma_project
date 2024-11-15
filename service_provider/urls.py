from django.urls import include, path
from .views import  BoostServiceCreateView


urlpatterns = [
    path('boost-service/', BoostServiceCreateView.as_view(), name='boost-service-create'),

]
