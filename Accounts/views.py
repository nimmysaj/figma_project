from rest_framework.views import APIView
from django.shortcuts import render
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

# Create your views here.

class LoginView(APIView):
    def post(self,request):
        try:
            user=User.objects.get(username=request.data.get('username'),password=request.data.get('password'))
            refresh=RefreshToken.for_user(user)
            access=refresh.access_token
            return Response({
            'message':"login successful",
            'refresh':str(refresh),
            'access':str(access)
            
            },status=status.HTTP_200_OK)
        except user.DoesNotExist :
            return Response({'message':"invalid"},status=status.HTTP_400_BAD_REQUEST)




