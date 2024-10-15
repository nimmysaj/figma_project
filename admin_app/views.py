from django.shortcuts import render
from rest_framework import permissions ,generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from Accounts.models import User, Franchise_Type ,Payment ,Franchisee
from .serializers import UserSerializer, FranchiseeSerializer ,PaymentSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Change based on your requirements
    def get_permissions(self):
        if self.action == 'create':  
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super(UserViewSet, self).get_permissions()     

# Franchisee ViewSet
class FranchiseeViewSet(viewsets.ModelViewSet):
    queryset = Franchisee.objects.all()
    serializer_class = FranchiseeSerializer
    permission_classes = [IsAuthenticated]  # Change based on your requirements

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class PaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer