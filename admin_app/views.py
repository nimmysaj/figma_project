from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Accounts.models import User, Franchisee,Franchise_Type
from .serializers import UserSerializer,FranchiseeSerializer,FranchiseTypeSerializer
from rest_framework.decorators import action
from django.db.models import Count
from rest_framework.pagination import PageNumberPagination



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
    
class FranchiseePagination(PageNumberPagination):
    page_size = 3  # Or any size you want for this view

class FranchiseeViewSet(viewsets.ModelViewSet):
    queryset = Franchisee.objects.all()
    serializer_class = FranchiseeSerializer    
    pagination_class = FranchiseePagination  # Add the custom pagination class here
    http_method_names = ['get'] 

    def get_queryset(self):
        # Annotate each franchise with the count of related dealers
        return Franchisee.objects.annotate(dealer_count=Count('dealer'))

    def list(self, request, *args, **kwargs):
        franchisees = self.get_queryset()  
        franchisees_count = franchisees.count()
        active_count = franchisees.filter(status='Active').count()  
        inactive_count = franchisees.filter(status='Inactive').count()  
        
         # Automatically apply pagination
        paginator = self.paginator
        paginated_franchisees = paginator.paginate_queryset(franchisees, request)

        # Serialize paginated data
        serializer = self.get_serializer(paginated_franchisees, many=True)

        # Return the response with counts and paginated data
        return paginator.get_paginated_response({
            "franchisees_count":franchisees_count,
            "active_franchisees": active_count, 
            "inactive_franchisees": inactive_count, 
            "franchisees": serializer.data 
        })
        # # Serialize all franchisees (you can filter if needed)
        # serializer = self.get_serializer(franchisees, many=True)

        # # Return the response with counts
        # return Response({
        #     "franchisees_count":franchisees_count,
        #     "active_franchisees": active_count, 
        #     "inactive_franchisees": inactive_count, 
        #     "franchisees": serializer.data 
        # })

class FranchiseTypeViewSet(viewsets.ModelViewSet):
    queryset = Franchise_Type.objects.all()
    serializer_class = FranchiseTypeSerializer    