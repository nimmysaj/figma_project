from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.response import Response
from Accounts.models import Customer, Subcategory,ServiceRegister,ServiceRequest
from .serializers import CustomerSerializer
from .serializers import Customerview_Serializer, SubcategorySerializer
from rest_framework.decorators import action
from .pagination import CustomerViewPagination

# Create your views here.




# ********************  ADD NEW USER *********************

class UserCreateView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def perform_create(self, serializer):
        # Auttomatically set is_customer = True in the serializer 
        serializer.save()





# ************************  USERS-USER MANAGEMENT  ************************* 

class CustomerListView(generics.ListAPIView):
    queryset = Customer.objects.all()             # Fetch all customers
    serializer_class = Customerview_Serializer
    pagination_class = CustomerViewPagination    # Apply custom pagination




# ********************* SUBCATEGORY - ADD NEW  **************************

class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status = status.HTTP_201_CREATED, headers = headers)
    
    def perform_create(self, serializer):
        serializer.save()


# Custom action for deletion (DELETE)
    @action(detail=False, methods=['delete'], url_path = 'delete')
    def delete_subcategory(self, request):
        subcategory_id = request.data.get('id')
        if not subcategory_id:
            return Response({"error":"subcategory_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        subcategory = get_object_or_404(Subcategory, id = subcategory_id)

        # First, delete all ServiceRequest instances related to this Subcategory  ----  Django's double underscore (__) notation to traverse relationships between models. 
        ServiceRequest.objects.filter(service__subcategory = subcategory).delete()          # service: This refers to a foreign key field in the ServiceRequest model that links to the ServiceRegister mode

        # Then, delete all ServiceRegister instances related to this Subcategory
        ServiceRegister.objects.filter(subcategory = subcategory).delete()        # subcategory is a foreign key on ServiceRegister

        # Now delete the Subcategory
        self.perform_destroy(subcategory)       # to delete the subcategory itself
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        instance.delete()


# custom action to get subcategories by category id
    @action(detail = False, methods = ['post'], url_path = 'by-category')
    def get_subcategories_by_category(self, request):
        category_id = request.data.get('id')

        if not category_id:
            return Response({"error": "category_id is required"}, status = status.HTTP_400_BAD_REQUEST)
        subcategories = Subcategory.objects.filter(category_id = category_id)
        serializer = self.get_serializer(subcategories, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)


 # Custom action for updating a subcategory (PUT/PATCH)
    @action(detail=False, methods = ['put', 'patch'], url_path='update')
    def update_subcategory(self, request):
        subcategory_id = request.data.get('id')

        if not subcategory_id:
            return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
        subcategory = get_object_or_404(Subcategory, id = subcategory_id)

        serializer = self.get_serializer(subcategory, data = request.data, partial=request.method == 'PATCH')
        serializer.is_valid(raise_exception = True)
        self.perform_update(serializer)
        return Response(serializer.data)
    def perform_update(self, serializer):
        serializer.save()