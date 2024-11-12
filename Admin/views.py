from django.shortcuts import render
from rest_framework import generics,status,permissions,authentication,views
from Accounts.models import Customer,Country_Codes,State,District,GENDER_CHOICES,Franchisee,ServiceProvider,Dealer,ServiceRequest,Complaint
from rest_framework.response import Response
from Admin.serializers import CustomerSerializer,BookingSerializer,ComplaintSerializer
from rest_framework.pagination import PageNumberPagination

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