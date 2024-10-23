from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from Accounts.models import Dealer, Franchisee, PaymentRequest
from Dealer.serializers import FranchiseeSerializer, PaymentRequestSerializer





# To list the franchisee details of the logged-in dealer

class DealerFranchiseeListView(generics.ListAPIView):
    serializer_class = FranchiseeSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated

    def get_queryset(self):
        # Get the logged-in dealer
        dealer = Dealer.objects.get(user=self.request.user)
        # Return the corresponding franchisee for this dealer
        return Franchisee.objects.filter(id=dealer.franchisee.id)
    


# To list the transaction history of dealer

class DealerPaymentHistoryView(generics.ListAPIView):
    serializer_class = PaymentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated

    def get_queryset(self):
        dealer = Dealer.objects.get(user=self.request.user)
        # Return the payment requests associated with this dealer
        return PaymentRequest.objects.filter(dealer=dealer).order_by('-created_at')