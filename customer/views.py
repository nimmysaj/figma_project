from rest_framework import generics
from .models import CustomerProfile
from .serializers import CustomerProfileSerializer

# Create Profile View
class CustomerProfileCreateView(generics.CreateAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
   # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# View and Update Profile View
class CustomerProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
   # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomerProfile.objects.filter(user=self.request.user)
