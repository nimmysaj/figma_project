from django.shortcuts import render

# Create your views here.
from Accounts.models import ServiceProvider
from Dealer.serializers import ServiceProviderSerializer,DealerLoginSerializer,LoginSerializer
from rest_framework import generics
from rest_framework import filters

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated



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




class LoginView(generics.GenericAPIView):

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # Generate a token for the authenticated user

        token, created = Token.objects.get_or_create(user=user)

        user_type = None

        if user.is_customer:

            user_type = "Customer"

        elif user.is_service_provider:

            user_type = "Service-Provider"

        elif user.is_dealer:

            user_type = "Dealer"

        elif user.is_franchisee:

            user_type = "Franchisee"  

        elif user.is_superuser:

            user_type = "Superuser" 

        elif user.is_staff:

            user_type = "Staff"    

        return Response({

            'message': 'Login successful',

            'token': token.key, # Include the token in the response

            'user_id': user.id,

            'email': user.email,

            'full_name': user.full_name,

            'user_type': user_type,

        }, status=status.HTTP_200_OK)