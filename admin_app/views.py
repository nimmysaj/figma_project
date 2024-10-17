from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Accounts.models import User, Franchisee,Franchise_Type
from .serializers import UserSerializer,FranchiseeSerializer,FranchiseTypeSerializer
from rest_framework.decorators import action



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user_id = request.data.get('id')  # Get the user ID from the request body
        if not user_id:
            return Response({"error": "ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = self.queryset.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class FranchiseeViewSet(viewsets.ModelViewSet):
    queryset = Franchisee.objects.all()
    serializer_class = FranchiseeSerializer    
    http_method_names = ['get']  # Only allow GET requests (list and retrieve)

    # @action(detail=True, methods=['get'])
    # def retrieve(self, request, pk=None):
    #     try:
    #         franchisee = Franchisee.objects.get(pk=pk)
    #         serializer = FranchiseeSerializer(franchisee)
    #         return Response(serializer.data)
    #     except Franchisee.DoesNotExist:
    #         return Response({"error": "Franchisee not found"}, status=404)
class FranchiseTypeViewSet(viewsets.ModelViewSet):
    queryset = Franchise_Type.objects.all()
    serializer_class = FranchiseTypeSerializer    