from django.shortcuts import render

# Create your views here.
from Accounts.models import ServiceProvider
from Dealer.serializers import ServiceProviderSerializer,DealerLoginSerializer
from rest_framework import generics
from rest_framework import filters

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
# from django.contrib.auth import authenticate,
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated




# get the list of all non verified service providers under the logged in dealer     
# class ServiceProviderVerificationListView(generics.ListAPIView):
    # authentication_classes=[TokenAuthentication]
    # permission_classes=[IsAuthenticated]
#     serializer_class=ServiceProviderSerializer
#     filter_backends=[filters.SearchFilter]
#     search_fields=['user__full_name','user__district__name']
    # def get_queryset(self):
    #     user = self.request.user
    #     queryset = ServiceProvider.objects.filter(
    #         verification_by_dealer='PENDING', 
    #         accepted_terms=True, 
    #         dealer__user=user)
            
    #     return queryset

# queryset = ServiceRegister.objects.annotate(request_count=Count('servicerequest'))

class DealerLoginView(generics.GenericAPIView):
    serializer_class = DealerLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate a token for the authenticated user
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'message': 'Login successful',
            'token': token.key, # Include the token in the response
            'user_id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'is_dealer': user.is_dealer,
        }, status=status.HTTP_200_OK)
    


from rest_framework import viewsets
from rest_framework.decorators import action

# class ServiceProviderViewSet(viewsets.ReadOnlyModelViewSet):
#     authentication_classes=[TokenAuthentication]
#     permission_classes=[IsAuthenticated]
#     queryset = ServiceProvider.objects.all()
#     serializer_class = ServiceProviderSerializer
#     filter_backends=[filters.SearchFilter]
#     search_fields=['user__full_name','user__district__name']

#     def get_queryset(self):
#         user = self.request.user
#         return ServiceProvider.objects.filter( 
#             accepted_terms=True, 
#             dealer__user=user)

#     @action(detail=True, methods=['get'])
#     def services(self, request, pk=None):
#         service_provider = self.get_object()
#         serializer = self.get_serializer(service_provider)
#         return Response(serializer.data)




class ServiceProviderViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__full_name', 'user__district__name']

    def get_queryset(self):
        user = self.request.user
        return ServiceProvider.objects.filter(
            accepted_terms=True,
            dealer__user=user
        )

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

