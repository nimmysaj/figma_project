from django.shortcuts import render
from rest_framework import generics,status,permissions,authentication,views
from Accounts.models import Customer,Country_Codes,State,District,GENDER_CHOICES,Franchisee,ServiceProvider,Dealer,ServiceRequest,Complaint,Invoice,Payment,Ad_category,Ad_Management
from rest_framework.response import Response
from Admin.serializers import CustomerSerializer,BookingSerializer,ComplaintSerializer,AdsManagementSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum
from datetime import datetime, timedelta 
import calendar
from rest_framework import filters

#pagination classes
class IncompleteBookingPaginator(PageNumberPagination):
    page_size=5
    page_query_param='page'
    max_page_size=5

class ComplaintPaginator(PageNumberPagination):
    page_size=6
    page_query_param='page'
    max_page_size=6

# Create your views here.

class AddNewUserView(generics.CreateAPIView):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get(self, request, *args, **kwargs):
        country_codes=Country_Codes.objects.all().values('country_name', 'calling_code','id')
        state=State.objects.all().values('name','id')
        district=District.objects.all().values('name','state','id')
        
        return Response({
            'gender_choices':GENDER_CHOICES,
            'country_codes':list(country_codes),
            'states':list(state),
            'districts':list(district)
        })

    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class AdminDashBoardView(views.APIView):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request,*args,**kwargs):
        total_franchise=Franchisee.objects.all().count()
        total_service_providers=ServiceProvider.objects.filter(status="Active",verification_by_dealer="APPROVED").count()
        total_dealers=Dealer.objects.all().count()
        total_users=Customer.objects.all().count()
        
        data={
            'total_franchise':total_franchise,
            'total_service_providers':total_service_providers,
            'total_dealers':total_dealers,
            'total_users':total_users
            }

        return Response(data=data)


class IncompleteBookingView(generics.ListAPIView):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=BookingSerializer
    queryset=ServiceRequest.objects.filter(work_status='pending').order_by('id')
    pagination_class=IncompleteBookingPaginator

class ComplaintsView(generics.ListAPIView):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    queryset=Complaint.objects.all().order_by('id')
    serializer_class=ComplaintSerializer
    pagination_class=ComplaintPaginator

class AdsManagementDashBoardView(views.APIView):
    def get(self,request,*args,**kwargs):
        today = datetime.today() 
        current_month_start = today.replace(day=1) 
        current_month_end = today  
        first_day_of_current_month = today.replace(day=1) 
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1) 
        previous_month_start = last_day_of_previous_month.replace(day=1) 
        previous_month_end = last_day_of_previous_month
        current_month_revenue = Payment.objects.filter( invoice__invoice_type='Ads', payment_date__range=[current_month_start, current_month_end] ).aggregate(total_revenue=Sum('amount_paid'))['total_revenue'] or 0.0
        previous_month_revenue = Payment.objects.filter( invoice__invoice_type='Ads', payment_date__range=[previous_month_start, previous_month_end] ).aggregate(total_revenue=Sum('amount_paid'))['total_revenue'] or 0.0
        total_ads_revenue = Payment.objects.filter( invoice__invoice_type='Ads' ).aggregate(total_revenue=Sum('amount_paid'))['total_revenue'] or 0.0
        total_ads=Ad_Management.objects.all().count()
        other_ad=['banner','pop_up','card']
        other_ads=Ad_Management.objects.filter(ad_category__ad_type__in=other_ad).count()
        current_month_ads = Ad_Management.objects.filter( created_date__range=[current_month_start, current_month_end],ad_category__ad_type__in=other_ad ).count() 
        previous_month_ads = Ad_Management.objects.filter( created_date__range=[previous_month_start, previous_month_end],ad_category__ad_type__in=other_ad ).count()
        if previous_month_ads > 0: 
            ads_percentage_difference = ((current_month_ads - previous_month_ads) / previous_month_ads) * 100 
            ads_change_type = "increase" if ads_percentage_difference > 0 else "decrease" 
        else: 
            ads_percentage_difference = 100.0 if current_month_ads > 0 else 0.0 
            ads_change_type = "increase" if current_month_ads > 0 else "no change"
        if previous_month_revenue > 0: 
            percentage_difference = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100 
            change_type = "increase" if percentage_difference > 0 else "decrease"
        else: 
            percentage_difference = 100.0 if current_month_revenue > 0 else 0.0
            change_type = "increase" if current_month_revenue > 0 else "no change"

        profile_boost=Ad_Management.objects.filter(ad_category__ad_type='profile_boost').count()
        current_month_ads = Ad_Management.objects.filter( created_date__range=[current_month_start, current_month_end],ad_category__ad_type='profile_boost').count() 
        previous_month_ads = Ad_Management.objects.filter( created_date__range=[previous_month_start, previous_month_end],ad_category__ad_type='profile_boost').count()
        if previous_month_ads > 0: 
            boost_ads_percentage_difference = ((current_month_ads - previous_month_ads) / previous_month_ads) * 100 
            boost_ads_change_type = "increase" if ads_percentage_difference > 0 else "decrease" 
        else: 
            boost_ads_percentage_difference = 100.0 if current_month_ads > 0 else 0.0 
            boost_ads_change_type = "increase" if current_month_ads > 0 else "no change"
        if previous_month_revenue > 0: 
            boost_percentage_difference = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100 
            boost_change_type = "increase" if percentage_difference > 0 else "decrease"
        else: 
            boost_percentage_difference = 100.0 if current_month_revenue > 0 else 0.0
            boost_change_type = "increase" if current_month_revenue > 0 else "no change"

            data={
                'ads_revenue':{
                'total_ads_revenue':total_ads_revenue,
                'percentage_diff':percentage_difference,
                'change_type':change_type},
                'total_ads':{
                    'ads':total_ads,
                    'difference':ads_percentage_difference,
                    'chage_type':ads_change_type
                },
                'other_ads':{
                    'other_ad_count':other_ads,
                    'difference':ads_percentage_difference,
                    'diff_type':ads_change_type
                },
                'profile_boost':{
                    'profile_boost_count':profile_boost,
                    'difference':boost_ads_percentage_difference,
                    'diff_type':boost_ads_change_type
                }
                }

        return Response(data=data)
    

class AdsCategoryView(views.APIView):
    def get(self,request,*args,**kwargs):
        qs=Ad_category.objects.all().values_list('ad_type')

        return Response(data={'ads_category':qs})


class AdsManagementView(generics.ListAPIView):
    serializer_class=AdsManagementSerializer
    queryset=Ad_Management.objects.all()
    filter_backends=[filters.SearchFilter]
    search_fields=['ad_category__ad_type']