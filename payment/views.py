from django.shortcuts import render
from Accounts.models import *
# Create your views here.
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404

class PaymentPageView(APIView):
    def get(self, request):
        # Render the payment page without additional context on GET
        return render(request, 'payment.html')

    def post(self, request):
        # Retrieve user_id from the request
        user_id = request.data.get('user_id')
        # Fetch the payment object with error handling
        obj = get_object_or_404(Payment, sender=user_id, payment_status="pending")
        amt = obj.invoice.total_amount * 100
        # Pass relevant data in the context
        context = {
            'amount': amt,
            'order_id': obj.order_id,
            'Key': "rzp_test_SPupR7nnkRh33c"
        }
        
        # Render the template with context
        return render(request, 'payment.html', context)