from rest_framework import generics, status
from .models import Category, Subcategory, Service_Type, Collar, ServiceProvider
from .serializers import CategorySerializer, SubCategorySerializer, ServiceTypeSerializer, CollarSerializer, ServiceProviderSerializer
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db.models import Q

# Create your views here.

# --------------------------------------------------- C A T E G O R I E S -------------------------------------------------------

# Category Create & View ['POST' & 'GET']
class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Category Edit, Delete ['PUT', 'PATCH' & 'DELETE']
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# --------------------------------------------------- S U B - C A T E G O R I E S -------------------------------------------------------

# SubCategory Create & View ['POST' & 'GET']
class SubCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = SubCategorySerializer

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        if category_id is None:
            raise ValueError("Category ID is missing.")
        return Subcategory.objects.filter(category_id=category_id)

    def create(self, request, *args, **kwargs):
        category_id = self.kwargs.get('category_id')
        data = request.data.copy()  # Make a mutable copy
        data['category'] = category_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# SubCategory Edit, Delete ['PUT', 'PATCH' & 'DELETE']
class SubCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubCategorySerializer

# --------------------------------------------------- S E A R C H - F U N C T I O N A L I T Y -------------------------------------------------------

# Combined Search View for Categories, Subcategories, and Service Providers
class SearchView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', None)
        
        if query:
            # Search for categories by title
            categories = Category.objects.filter(title__icontains=query)
            
            # If categories are found, return category and subcategory details
            if categories.exists():
                category_response = []
                for category in categories:
                    subcategories = Subcategory.objects.filter(category=category)  # Get subcategories for this category
                    category_response.append({
                        'category': CategorySerializer(category).data,
                        'subcategories': SubCategorySerializer(subcategories, many=True).data  # Only subcategories, no service providers
                    })
                return Response({
                    'categories': category_response
                })
            
            # Search for subcategories by title
            subcategories = Subcategory.objects.filter(title__icontains=query)
            
            # If subcategories are found, return subcategory and service provider details
            if subcategories.exists():
                subcategory_response = []
                for subcategory in subcategories:
                    service_providers = ServiceProvider.objects.filter(subcategory=subcategory)  # Get service providers for this subcategory
                    subcategory_response.append({
                        'subcategory': SubCategorySerializer(subcategory).data,
                        'service_providers': ServiceProviderSerializer(service_providers, many=True).data  # Only service providers for the subcategory
                    })
                return Response({
                    'subcategories': subcategory_response
                })

            # Search for service providers by name, description, or contact_info
            service_providers = ServiceProvider.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(contact_info__icontains=query)
            )

            # If service providers are found, return their details only
            if service_providers.exists():
                return Response({
                    'service_providers': ServiceProviderSerializer(service_providers, many=True).data
                })

        # If no valid query is provided
        return Response({"message": "Please provide a valid search term."}, status=status.HTTP_400_BAD_REQUEST)

# --------------------------------------------------- S E R V I C E - T Y P E -------------------------------------------------------

# Views for Service_Type
class ServiceTypeListCreateView(generics.ListCreateAPIView):
    queryset = Service_Type.objects.all()
    serializer_class = ServiceTypeSerializer

class ServiceTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service_Type.objects.all()
    serializer_class = ServiceTypeSerializer

# --------------------------------------------------- C O L L A R -------------------------------------------------------

# Views for Collar
class CollarListCreateView(generics.ListCreateAPIView):
    queryset = Collar.objects.all()
    serializer_class = CollarSerializer

class CollarDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Collar.objects.all()
    serializer_class = CollarSerializer

# --------------------------------------------------- S E R V I C E - P R O V I D E R -------------------------------------------------------

# Create and List Service Providers
class ServiceProviderListCreateView(generics.ListCreateAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer

# Retrieve, Update, and Delete Service Providers
class ServiceProviderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
