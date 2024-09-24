from django.shortcuts import render

from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from customer.serializers import UserSerializer,OTPSerializer
from customer.models import User,OTP



class UserRegistrationView(generics.CreateAPIView):

    serializer_class = UserSerializer

    def post(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"User Registered Successfully! OTP sent to your email."}, status=status.HTTP_201_CREATED)
    
   
class OTPVerifyView(generics.GenericAPIView):

    serializer_class = OTPSerializer
    # permission_classes = [AllowAny]

    def post(self,request,*args,**kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        tokens = serializer.generate_jwt_token(user)

        return Response({"message":"OTP verified successfully","tokens":tokens},status=status.HTTP_200_OK)