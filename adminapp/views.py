from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import ServiceRequest
from .serializers import ServiceRequestSerializer
from django.http import Http404

@api_view(['GET'])
def get_service_request_by_id(request, id):
    try:
        service_request = ServiceRequest.objects.get(id=id)
    except ServiceRequest.DoesNotExist:
        raise Http404("Service Request not found")
    
    serializer = ServiceRequestSerializer(service_request)
    return Response(serializer.data)
