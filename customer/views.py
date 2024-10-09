from rest_framework import generics, status
from .models import Customer
from .serializers import CustomerSerializer
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

class CustomerProfileCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Pass the current user to the serializer context
        serializer.save()

# List all customer profiles (GET)
class CustomerProfileListView(generics.ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Optionally filter customer profiles based on the user or other criteria."""
        # If you need to filter profiles by the logged-in user in the future
        # return CustomerProfile.objects.filter(user=self.request.user)
        return super().get_queryset()

# Retrieve, Update (PUT or PATCH), and Delete (DELETE) a specific customer profile (GET, PUT, PATCH, DELETE)
class CustomerProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]
    # permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Override to ensure the customer profile is retrieved properly."""
        # If you want to filter based on user (when user handling is needed)
        # return get_object_or_404(CustomerProfile, user=self.request.user, pk=self.kwargs['pk'])
        return super().get_object()
