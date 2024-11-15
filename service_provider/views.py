from decimal import Decimal
from rest_framework.generics import CreateAPIView
from django.shortcuts import get_object_or_404, render
from django.db.models import Avg,Sum
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics,viewsets
from Accounts.models import ServiceProvider, ServiceRequest, User,Payment,CustomerReview,AdManagement,AdCategory
from service_provider.permissions import IsOwnerOrAdmin
from .serializers import BoostServiceSerializer
from django.utils.encoding import smart_bytes, smart_str
from twilio.rest import Client
from rest_framework.decorators import action
from copy import deepcopy
# Create your views here.



class BoostServiceCreateView(generics.CreateAPIView):
    queryset = AdManagement.objects.all()
    serializer_class = BoostServiceSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)