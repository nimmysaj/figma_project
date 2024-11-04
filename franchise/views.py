from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import serializers
from rest_framework import generics
# from .serializers import FranchiseeLoginSerializer
from Accounts.models import User,Dealer,Franchisee
from django.utils import timezone

# Create your views here.

# Combining the two list and return as serializer response
class CombinedDetailsSerializer(serializers.Serializer):
    dealer_details = serializers.ListField(child = serializers.DictField())
    additional_details = serializers.ListField(child = serializers.DictField())

# Percentage Calculation function
class PercentageCalculator:
    @staticmethod
    def calculate_percentage(current_month_count,last_month_count):
        if last_month_count == 0:
            return 100 if current_month_count > 0 else 0
        percentage_change = ((current_month_count - last_month_count)/last_month_count) * 100

        if percentage_change < 0:
            return percentage_change / 100
        else:
            return percentage_change
        
class DealerView(APIView):
    permission_class =[IsAuthenticated]

    def get(self, request,*args, **kwargs):
        try:
            
            franchisee = Franchisee.objects.get(user_id=request.user.id)
            # Find the Dealers for the authenticated user (franchisee)
            query = Q(franchisee_id = franchisee.id)
            queryset = Dealer.objects.filter(query)
            if not queryset.exists():
                return Response(
                    {"message": "No dealers are added."},
                        status=status.HTTP_404_NOT_FOUND
                )

            # Taken the total dealers,total active dealers,total inactive dealers
            total_dealers = queryset.count()
            total_active_dealers = Dealer.objects.filter(Q(query) & Q(status = 'Active')).count()
            total_inactive_dealers = Dealer.objects.filter(Q(query) & Q(status = 'Inactive')).count()

            # Calculating the Percentage of total dealers
            current_month_dealers = Dealer.objects.filter(Q(query) & Q(created_date__month = timezone.now().month)).count()
            last_month_dealers = Dealer.objects.filter(Q(query) & Q(created_date__month = timezone.now().month -1)).count()
            dealers_percentage=PercentageCalculator.calculate_percentage(current_month_dealers,last_month_dealers)
            
            # Calculating the Percentage of active dealers
            active_query = Q(query) & Q(status = 'Active')
            current_month_active = Dealer.objects.filter(Q(active_query) & Q(created_date__month = timezone.now().month)).count()
            last_month_active = Dealer.objects.filter(Q(active_query) & Q(created_date__month = timezone.now().month-1)).count()
            active_dealers_percentage = PercentageCalculator.calculate_percentage(current_month_active,last_month_active)

            # Calculating the Percentage of Inactive dealers
            inactive_query = Q(query) & Q(status='Inactive')
            current_month_inactive = Dealer.objects.filter(Q(inactive_query) & Q(created_date__month = timezone.now().month)).count()
            last_month_inactive = Dealer.objects.filter(Q(inactive_query) & Q(created_date__month = timezone.now().month-1)).count()
            inactive_dealers_percentage = PercentageCalculator.calculate_percentage(current_month_inactive,last_month_inactive)

            additional_details = []
            additional_details = [
                    {'total_dealers': total_dealers,
                    'total_dealers_perc':dealers_percentage,
                    'total_active': total_active_dealers,
                    'active_dealers_perc':active_dealers_percentage,
                    'total_inactive' : total_inactive_dealers,
                    'inactive_dealers_perc':inactive_dealers_percentage
                    }
            ]
            
            # Taken the details of the Dealers
            dealer_details = []
            for dealers in queryset:
                dealer_user = User.objects.get(id=dealers.user_id)
                dealer_profile = Dealer.objects.get(id = dealers.id)
                dealer_details.append({
                        'name':dealer_user.full_name,
                        'custom_id': dealer_profile.custom_id,
                        'service_providers':dealer_profile.service_providers,
                        'location': dealer_user.district.name if dealer_user.district else 'Unknown Location',
                        'contact':dealer_user.phone_number,
                        'email':dealer_user.email,
                        'status':dealer_profile.status,
                })
                serializer = CombinedDetailsSerializer({
                    'additional_details':additional_details,
                    'dealer_details':dealer_details
                })
                
            return Response(serializer.data, status=200)

        except Exception as e:
            # Log the error for debugging
            print(f"Error fetching dealers: {e}")
            return Response(
                {"error": "An error occurred while retrieving dealers."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DealerSearchView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access
    def get(self,request):
        try:
            franchisee = Franchisee.objects.get(user_id=request.user.id)
            query = request.query_params.get('search',None)
            if not query:
                return Response(
                        {"message": "Please provide dealer name in search bar."},
                        status=status.HTTP_404_NOT_FOUND
                )
            else:
                dealers_list = User.objects.filter(Q(full_name__icontains = query) | Q(district__name__icontains = query))     
                if dealers_list.exists():
                    dealers_details = []
                    for rec in dealers_list:
                        try:
                            dealers_profile = Dealer.objects.get(Q(user_id = rec.id) & Q(franchisee_id = franchisee.id))
                            dealer_user = User.objects.get(id = rec.id) 
                            dealers_details.append({
                                    'name':dealer_user.full_name,
                                    'custom_id': dealers_profile.custom_id,
                                    'service_providers':dealers_profile.service_providers,
                                    'location': dealer_user.district.name if dealer_user.district else 'Unknown Location',
                                    'contact':dealer_user.phone_number,
                                    'email':dealer_user.email,
                                    'status':dealers_profile.status,
                            }) 
                        except Dealer.DoesNotExist:
                            return Response({"message": "No dealers are added."})
                   
                    return Response(dealers_details,status=200)
                else:
                    return Response(
                    {"message": "No dealers are added."},
                        status=status.HTTP_404_NOT_FOUND
                    )
        except Exception as e:
            # Log the error for debugging
            print(f"Error fetching dealers: {e}")
            return Response(
                {"error": "An error occurred while retrieving dealers."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )            