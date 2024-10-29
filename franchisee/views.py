from rest_framework.response import Response
from rest_framework import status, generics
from Accounts.models import ServiceRegister
from .serializers import ServiceRegisterSerializer,FranchiseeLoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

# submit new service

class SubmitServiceView(generics.UpdateAPIView):  
    queryset = ServiceRegister.objects.all()
    serializer_class = ServiceRegisterSerializer
    # permission_classes = [IsAuthenticated]


    def update(self, request, *args, **kwargs):
        service = self.get_object()

    # Check if the service is already submitted
        if service.status == 'Submitted':
            return Response(
                {"error": "Service is already submitted."},
                status=status.HTTP_400_BAD_REQUEST
            )

        service.status = 'Submitted'
        service.save()
        return Response({"message": "Service submitted successfully."}, status=status.HTTP_200_OK)

# save as draft

class SaveDraftServiceView(generics.UpdateAPIView):    
    queryset = ServiceRegister.objects.all()
    serializer_class = ServiceRegisterSerializer


    def update(self, request, *args, **kwargs):
        service = self.get_object()
        service.status = 'Draft'
        service.save()
        return Response({"message": "Service saved as draft."}, status=status.HTTP_200_OK)

#delete current form

class DeleteServiceView(generics.DestroyAPIView):
    queryset = ServiceRegister.objects.all()
    serializer_class = ServiceRegisterSerializer


    def destroy(self, request, *args, **kwargs):
        service = self.get_object()
        service.status = 'Deleted'
        service.save()
        return Response({"message": "Service deleted successfully."}, status=status.HTTP_200_OK)
    



class FranchiseeLoginView(generics.GenericAPIView):
    serializer_class = FranchiseeLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate a token for the authenticated user
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'message': 'Login successful',
            'token': token.key,  # Include the token in the response
            'user_id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'is_franchisee': user.is_franchisee,
        }, status=status.HTTP_200_OK)