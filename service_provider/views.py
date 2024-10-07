from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from Accounts.models import ServiceProvider, User, Payment, Invoice
from service_provider.serializers import ServiceProviderSerialzer, UserSerializer, PaymentSerializer, InvoiceSerializer
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
import razorpay



##################### SERVICE PROVIDER PROFILE ########################################################

class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset =ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerialzer
    #permission_class =[IsAuthenticated]













  
#################### PAYMENT ####################################


class InitiatePaymentView(APIView):
    
    def post(self, request):
        invoice_id = request.data.get('invoice_id')


        if not invoice_id:
            return Response({"error": "Invoice ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the invoice
            invoice = Invoice.objects.get(id=invoice_id)

            # Check if the invoice is in a valid state for payment
            if invoice.payment_status != 'pending':
                return Response({"error": "Invoice cannot be paid."}, status=status.HTTP_400_BAD_REQUEST)
        # try:
        #     # Fetch the invoice using the provided invoice_id
        #     invoice = get_object_or_404(Invoice, id=invoice_id)

            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

            # Prepare Razorpay order data
            order_amount = int(invoice.total_amount * 100)  # Amount in paise
            order_data = {
                'amount': order_amount,
                'currency': 'INR',
                'receipt': f'invoice_rcpt_{invoice.id}',
                'notes': {'invoice_id': str(invoice.id), 'receiver': str(invoice.receiver)},
            }

            # Create Razorpay order
            razorpay_order = client.order.create(data=order_data)

            # Save a new Payment instance linked to this invoice using the serializer
            payment_data = {
                'invoice': invoice.id,  # Use the ID as the foreign key reference
                'sender': invoice.sender.id,
                'receiver': invoice.receiver.id,
                'transaction_id': razorpay_order['id'],
                'amount_paid': invoice.total_amount,
                'payment_method': 'razorpay',
                'payment_status': 'pending'
            }
            payment_serializer = PaymentSerializer(data=payment_data)
            payment_serializer.is_valid(raise_exception=True)
            payment = payment_serializer.save()

            # Return the serialized payment details along with the order ID
            return Response({
                'order_id': razorpay_order['id'],
                'amount': order_amount,
                'currency': 'INR',
                'invoice': InvoiceSerializer(invoice).data,
                "message": "Payment initiated successfully.",
                'payment': payment_serializer.data
            }, status=status.HTTP_201_CREATED)

        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmPaymentView(APIView):
    

    def post(self, request):
        # Retrieve data from the request payload
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = request.data.get('razorpay_signature')
        invoice_id = request.data.get('invoice_id')

        # Validate the received payment details
        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature, invoice_id]):
            return Response({"error": "Missing required payment details."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the invoice and corresponding payment
        invoice = get_object_or_404(Invoice, id=invoice_id)
        payment = get_object_or_404(Payment, invoice=invoice, transaction_id=razorpay_order_id)

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

        # Verify the payment signature
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Payment signature verification failed."}, status=status.HTTP_400_BAD_REQUEST)

        # Capture the payment if verification is successful
        try:
            # Capture the payment (if needed)
            client.payment.capture(razorpay_payment_id, int(payment.amount_paid * 100))

            # Update payment status and invoice status
            payment.transaction_id = razorpay_payment_id
            payment.payment_status = 'completed'
            payment.payment_date = timezone.now()
            payment.save()

            invoice.payment_status = 'paid'
            invoice.save()

            # Serialize the updated payment and invoice details
            payment_serializer = PaymentSerializer(payment)
            invoice_serializer = InvoiceSerializer(invoice)

            return Response({
                "message": "Payment confirmed successfully!",
                "payment": payment_serializer.data,
                "invoice": invoice_serializer.data,
                "amount": invoice.total_amount,
                "status": "Paid"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
