from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .permissions import IsFranchiseAdminOrOwner
from .serializers import ServiceRegisterSerializer
from rest_framework import status
from rest_framework.response import Response
from .serializers import FranchiseeLoginSerializer
from rest_framework import generics
from Accounts.models import ServiceRegister
from .serializers import ServiceRegisterSerializer

class AddServiceView(generics.CreateAPIView):
    queryset = ServiceRegister.objects.all()
    serializer_class = ServiceRegisterSerializer
    permission_classes = [IsAuthenticated, IsFranchiseAdminOrOwner]

def add_service(request):
    if request.method == 'POST':
        serializer = ServiceRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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