from django.shortcuts import render

# Create your views here.

from rest_framework import generics,filters,serializers
from Accounts.models import Dealer,ServiceProvider
from franchise.serializers import DealerSerializer,FranchiseeLoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets
from rest_framework.decorators import action
from Dealer.serializers import ServiceProviderSerializer

# get the dealer details, also perform edit function,have search functionality using query params

class DealerdetailView(APIView):
    def get(self,request,*args,**kwargs):
        id=request.data.get("dealer_id")
        dealer=request.query_params.get('dealer')
        if id:
            try:
                qs=Dealer.objects.get(custom_id=id)
                serializer_instance=DealerSerializer(qs)
                return Response(data=serializer_instance.data,status=status.HTTP_200_OK)
            except:
                return Response(data={"message":"Dealer Not found"},status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                qs=Dealer.objects.get(user__full_name=dealer)
                serializer_instance=DealerSerializer(qs)
                return Response(data=serializer_instance.data,status=status.HTTP_200_OK)
            except:
                return Response(data={"message":"Dealer Not found"},status=status.HTTP_400_BAD_REQUEST)
            
    def put(self, request, *args, **kwargs): 
        id = request.data.get("dealer_id") 
        dealer = request.query_params.get('dealer') 
        if id: 
            try: 
                qs = Dealer.objects.get(custom_id=id) 
            except Dealer.DoesNotExist: 
                return Response(data={"message": "Dealer Not found"}, status=status.HTTP_404_NOT_FOUND) 
        elif dealer: 
            try:
                qs = Dealer.objects.get(user__full_name=dealer) 
            except Dealer.DoesNotExist: 
                return Response(data={"message": "Dealer Not found"}, status=status.HTTP_404_NOT_FOUND) 
            else: return Response(data={"message": "Dealer ID or dealer query parameter is required."}, status=status.HTTP_400_BAD_REQUEST) 
        serializer_instance = DealerSerializer(qs, data=request.data, partial=True)
        if serializer_instance.is_valid(): 
            serializer_instance.save() 
            return Response(data=serializer_instance.data, status=status.HTTP_200_OK) 
        else: return Response(data=serializer_instance.errors, status=status.HTTP_400_BAD_REQUEST)


class FranchiseServiceProviderViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__full_name', 'user__district__name']

    @action(detail=False, methods=['post'])
    def services(self, request):
        service_provider_id = request.data.get('service_provider_id')
        
        if not service_provider_id:
            return Response({'error': 'Service Provider ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service_provider = ServiceProvider.objects.get(custom_id=service_provider_id)
        except ServiceProvider.DoesNotExist:
            return Response({'error': 'Service Provider not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(service_provider)
        return Response(serializer.data)