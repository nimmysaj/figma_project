# views.py in your app directory (e.g., franchisee/views.py)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .permissions import IsFranchiseAdminOrOwner
from .serializers import ServiceRegisterSerializer
from rest_framework import status
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsFranchiseAdminOrOwner])

def add_service(request):
    if request.method == 'POST':
        serializer = ServiceRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
