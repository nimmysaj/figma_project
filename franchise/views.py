from django.shortcuts import render

# Create your views here.

from rest_framework import generics,filters
from Accounts.models import Dealer
from franchise.serializers import DealerSerializer,FranchiseeLoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

# get the dealer details, also perform edit function
class DealerDetailView(generics.RetrieveUpdateAPIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    queryset = Dealer.objects.all()
    serializer_class = DealerSerializer
    lookup_field = 'pk'


# implemented search functionality in dealer details page
class DealerSearchView(generics.ListAPIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    serializer_class = DealerSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__full_name']

    def get_queryset(self):
        user = self.request.user
        return Dealer.objects.filter(franchisee__user=user)


class FranchiseeLoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FranchiseeLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            franchisee = serializer.validated_data['franchisee']
            token,created=Token.objects.get_or_create(user=user)
            return Response({
                'token':token.key,
                'message': 'Login successful',
                'user_id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_farnchisee': user.is_franchisee,
                'franchisee':franchisee.custom_id
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

