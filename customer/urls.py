from django.urls import path
from customer import views


urlpatterns = [

    path("register/",views.UserRegistrationView.as_view(),name="register"),
    path("otp/",views.OTPVerifyView.as_view(),name="verify_otp")
    

]


