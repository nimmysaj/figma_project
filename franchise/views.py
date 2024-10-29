from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import FranchiseeLoginSerializer

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

