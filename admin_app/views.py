from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Franchise_Type
from rest_framework import serializers
from .serializer import Franchise_Type_Serializer
from rest_framework import status

# Create your views here.
class Franchise_TypeView(APIView):
    def get(self, request):
        # Retrieve all Person objects
        fnt = Franchise_Type.objects.all()
        serializer = Franchise_Type_Serializer(fnt, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Create a new Person object
        serializer = Franchise_Type_Serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # Update an existing Person object
        try:
            fnt = Franchise_Type.objects.get(id=request.data['id'])
        except Franchise_Type.DoesNotExist:
            return Response({"error": "Franchisee type not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = Franchise_Type_Serializer(fnt, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        # Partially update an existing Person object
        try:
            fnt = Franchise_Type.objects.get(id=request.data['id'])
        except Franchise_Type.DoesNotExist:
            return Response({"error": "Franchisee not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = Franchise_Type_Serializer(fnt, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Delete a Person object
        try:
            fnt = Franchise_Type.objects.get(id=request.data['id'])
        except Franchise_Type.DoesNotExist:
            return Response({"error": "Franchisee not found"}, status=status.HTTP_404_NOT_FOUND)

        fnt.delete()
        return Response({"message": "Franchisee deleted successfully"}, status=status.HTTP_204_NO_CONTENT)