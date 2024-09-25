from rest_framework import generics
from .models import CustomerProfile
from .serializers import CustomerProfileSerializer
from rest_framework.permissions import AllowAny

# Create a new customer profile (POST)
class CustomerProfileCreateView(generics.CreateAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    permission_classes = [AllowAny]
    # permission_classes = [permissions.IsAuthenticated]

# List all customer profiles (GET)
class CustomerProfileListView(generics.ListAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    permission_classes = [AllowAny]
    # permission_classes = [permissions.IsAuthenticated]

# Retrieve, Update (PUT or PATCH) and Delete (DELETE) a specific customer profile (GET, PUT, PATCH, DELETE)
class CustomerProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    permission_classes = [AllowAny]
