from rest_framework import generics, status
from .models import Category, Subcategory, ServiceProvider, Complaint
from .serializers import CategorySerializer, SubCategorySerializer, ServiceProviderSerializer, ComplaintSerializer
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

# --------------------------------------------------- S U B - C A T E G O R I E S -------------------------------------------------------

# SubCategory Create & View ['POST' & 'GET']
class SubCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = SubCategorySerializer

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        if category_id is None:
            raise ValueError("Category ID is missing.")
        return Subcategory.objects.filter(category_id=category_id)

# --------------------------------------------------- S E A R C H - F U N C T I O N A L I T Y -------------------------------------------------------
class SearchView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', None)
        
        if query:
            categories = Category.objects.filter(                           # Search for categories by name
                Q(name__icontains=query) & Q(status='Active')
            )
            
            # If categories are found, return category details only
            if categories.exists():
                return Response({
                    'categories': CategorySerializer(categories, many=True).data
                })
            
            # Search for subcategories by name
            subcategories = Subcategory.objects.filter(
                Q(name__icontains=query) & Q(status='Active')
            )
            
            # If subcategories are found, return subcategory details only
            if subcategories.exists():
                return Response({
                    'subcategories': SubCategorySerializer(subcategories, many=True).data
                })

            # Search for service providers by name, description, or contact_info
            service_providers = ServiceProvider.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(contact_info__icontains=query),
                status='Active'
            )

            # If service providers are found, return their details only
            if service_providers.exists():
                return Response({
                    'service_providers': ServiceProviderSerializer(service_providers, many=True).data
                })

        # If no valid query is provided
        return Response({"message": "Please provide a valid search term."}, status=status.HTTP_400_BAD_REQUEST)

# --------------------------------------------------- S E R V I C E - P R O V I D E R -------------------------------------------------------

# Create and List Service Providers
class ServiceProviderListCreateView(generics.ListCreateAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer

# --------------------------------------------------- C O M P L A I N T - F O R M -------------------------------------------------------

class CreateComplaintView(generics.ListCreateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
