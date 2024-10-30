from django.shortcuts import render

# Create your views here.

from rest_framework import generics,filters
from Accounts.models import Dealer
from franchise.serializers import DealerSerializer


# get the dealer details 
class DealerDetailView(generics.RetrieveAPIView):
    queryset = Dealer.objects.all()
    serializer_class = DealerSerializer
    lookup_field = 'pk'


# implemented search functionality in dealer details page
class DealerSearchView(generics.ListAPIView):
    serializer_class = DealerSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__full_name']

    def get_queryset(self):
        user = self.request.user
        return Dealer.objects.filter(franchisee__user=user)
