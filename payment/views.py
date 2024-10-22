from django.shortcuts import render

# Create your views here.
import razorpay
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from customer.models import Invoice, Payment
from .serializers import InvoiceSerializer, PaymentSerializer
import razorpay
import json
from django.urls import reverse
import hmac
import hashlib
from decimal import Decimal




class CreatePaymentOrderAPIView(APIView):
    def post(self, request):
        try:
            print("Received data:", request.data)

            invoice_id = request.data.get('invoice_id')
            payment_type = request.data.get('payment_type')  # 'full' or 'partial'

            if not invoice_id:
                print("Error: Missing invoice_id")
                return Response({"error": "invoice_id is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                invoice = Invoice.objects.get(id=invoice_id)
                print(f"Invoice found: {invoice}")
            except Invoice.DoesNotExist:
                print(f"Error: Invoice with id {invoice_id} not found")
                return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            print("Razorpay client initialized successfully")

            # Handling partial payment
            if payment_type == 'partial':
                print("Processing partial payment")

                # Allow only if the invoice status is 'pending'
                if invoice.payment_status != 'pending':
                    return Response({"error": "Partial payment is allowed only when the invoice status is 'pending'."}, status=status.HTTP_400_BAD_REQUEST)
                
                partial_amount = invoice.partial_amount or 0  # Default to 0 if None
                payment_amount = (invoice.payment_balance * Decimal('0.4'))  # Calculate 40% of the payment balance
                print(payment_amount)

                # Validate that partial amount is not greater than total_amount
                if partial_amount + payment_amount > invoice.payment_balance:
                    return Response({"error": "Partial amount cannot be greater than the total amount."}, status=status.HTTP_400_BAD_REQUEST)

                print(f"Partial amount: {partial_amount}, Payment amount (in paise): {payment_amount * 100}")
                #payment_amount = int(partial_amount * 100)  # Convert to paise
                #print(f"Partial amount: {partial_amount}, Payment amount (in paise): {payment_amount}")

                # Calculate remaining balance after partial payment
                remaining_amount = invoice.payment_balance - payment_amount
                print(f"Remaining amount: {remaining_amount}")
                
                

                # Update the invoice with the new remaining amount and payment status
                invoice.payment_status = 'partially_paid'
                invoice.payment_balance = remaining_amount
                invoice.partial_amount = partial_amount + payment_amount
                print(f"The invoice table partial amount:{invoice.partial_amount}")
                payment_amount = int(payment_amount * 100)
                print(payment_amount)

                # Save the invoice after updates
                invoice.save(update_fields=['payment_status', 'payment_balance', 'partial_amount'])
                print(f"Invoice updated with remaining amount: {remaining_amount}, Status: Partially Paid")

            # Handling full payment
            elif payment_type == 'full':
                print("Processing full payment")

                # Disallow full payment if the invoice status is already 'paid'
                if invoice.payment_status == 'paid':
                    return Response({"error": "Full payment is not allowed when the invoice is already marked as 'paid'."}, status=status.HTTP_400_BAD_REQUEST)

                if invoice.payment_status == 'partially_paid':
                    payment_amount = int(invoice.payment_balance * 100)  # Full remaining balance
                    print(f"Full payment for remaining balance: {payment_amount}")
                else:
                    payment_amount = int(invoice.payment_balance * 100)  # Full payment from the start
                    print(f"Full payment from start: {payment_amount}")
                
                # If full payment is made, update the invoice to 'paid'
                invoice.payment_status = 'paid'

                # Save the invoice with the new status
                invoice.save(update_fields=['payment_status'])
                print("Invoice updated to Paid status")

            # Create the order in Razorpay
            payment_data = {
                'amount': payment_amount,
                'currency': 'INR',
                'receipt': f"inv_{invoice.id}",
                'payment_capture': 1,  # Auto capture the payment
            }
            print(f"Creating Razorpay order with data: {payment_data}")
            order = client.order.create(data=payment_data)
            print(f"Razorpay order created successfully: {order}")

            # Now create the Payment record using the Razorpay order ID
            payment = Payment.objects.create(
                invoice=invoice,
                sender=invoice.sender,
                receiver=invoice.receiver,
                transaction_id=order['id'],  # Razorpay order_id as transaction ID
                order_id=order['id'],         # Razorpay order_id
                amount_paid=payment_amount / 100,  # Convert paise back to rupees
                payment_method='razorpay',
                payment_status='pending',
            )
            print(f"Payment record created: {payment}")

            # Serialize payment and invoice data
            payment_serializer = PaymentSerializer(payment)
            invoice_serializer = InvoiceSerializer(invoice)

            print("Sending successful response")
            return Response({
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'invoice': invoice_serializer.data,
                'payment': payment_serializer.data,
            }, status=status.HTTP_201_CREATED)

        except Invoice.DoesNotExist:
            print("Error: Invoice not found")
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



def payment_view(request):
    return render(request, 'payment/payment.html', {
        'razorpay_key': settings.RAZORPAY_KEY_ID  # Pass the Razorpay key to the template
    })
   
#without return  invoice details,  working code
"""

class VerifyPaymentAPIView(APIView):
    def post(self, request):
        try:
            razorpay_payment_id = request.data.get('razorpay_payment_id')
            razorpay_order_id = request.data.get('razorpay_order_id')
            razorpay_signature = request.data.get('razorpay_signature')

            if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
                return Response({"error": "Required fields are missing"}, status=status.HTTP_400_BAD_REQUEST)

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Fetch payment details from Razorpay
            payment_details = client.payment.fetch(razorpay_payment_id)

            # Signature verification
            generated_signature = hmac.new(
                bytes(settings.RAZORPAY_KEY_SECRET, 'utf-8'),
                msg=bytes(f"{razorpay_order_id}|{razorpay_payment_id}", 'utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()

            if generated_signature != razorpay_signature:
                return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the payment record using the order ID
            try:
                payment_record = Payment.objects.get(order_id=razorpay_order_id)
            except Payment.DoesNotExist:
                return Response({'error': 'Payment with this order ID not found'}, status=status.HTTP_404_NOT_FOUND)

            # Update payment record with Razorpay details
            payment_record.transaction_id = razorpay_payment_id
            payment_record.signature = razorpay_signature

            # Process payment status
            
            payment_status = payment_details['status']
            if payment_status == 'captured':
                payment_record.mark_completed()  # Set status to 'completed'
            elif payment_status == 'failed':
                payment_record.mark_failed()
            else:
                payment_record.payment_status = 'pending'
                

            payment_record.save()

            return Response({
                'transaction_id': payment_record.transaction_id,
                'order_id': razorpay_order_id,
                'amount': payment_record.amount_paid,
                'status': payment_record.payment_status,
                'payment_details': payment_details
            }, status=status.HTTP_200_OK)

        except razorpay.errors.BadRequestError as e:
            return Response({'error': 'Bad Request: {}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

  """
  # with invoice details working code
class VerifyPaymentAPIView(APIView):
    def post(self, request):
        try:
            razorpay_payment_id = request.data.get('razorpay_payment_id')
            razorpay_order_id = request.data.get('razorpay_order_id')
            razorpay_signature = request.data.get('razorpay_signature')

            if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
                return Response({"error": "Required fields are missing"}, status=status.HTTP_400_BAD_REQUEST)

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Fetch payment details from Razorpay
            payment_details = client.payment.fetch(razorpay_payment_id)

            # Signature verification
            generated_signature = hmac.new(
                bytes(settings.RAZORPAY_KEY_SECRET, 'utf-8'),
                msg=bytes(f"{razorpay_order_id}|{razorpay_payment_id}", 'utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()

            if generated_signature != razorpay_signature:
                return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the payment record using the order ID with the related invoice details
            try:
                payment_record = Payment.objects.select_related('invoice').get(order_id=razorpay_order_id)
            except Payment.DoesNotExist:
                return Response({'error': 'Payment with this order ID not found'}, status=status.HTTP_404_NOT_FOUND)

            # Update payment record with Razorpay details
            payment_record.transaction_id = razorpay_payment_id
            payment_record.signature = razorpay_signature

            # Process payment status
            payment_status = payment_details['status']
            if payment_status == 'captured':
                payment_record.mark_completed()  # Set status to 'completed'
            elif payment_status == 'failed':
                payment_record.mark_failed()
            else:
                payment_record.payment_status = 'pending'

            payment_record.save()

            # Fetch the related invoice details
            invoice = payment_record.invoice

            # Return both payment and invoice details in the response
            return Response({
                'transaction_id': payment_record.transaction_id,
                'order_id': razorpay_order_id,
                'amount': payment_record.amount_paid,
                'status': payment_record.payment_status,
                'payment_details': payment_details,
                'invoice': {
                    'invoice_number': invoice.invoice_number,
                    'invoice_type': invoice.invoice_type,
                    'price': invoice.price,
                    'total_amount': invoice.total_amount,
                    'payment_balance':invoice.payment_balance,
                    'payment_status': invoice.payment_status,
                    'partial_amount': invoice.partial_amount,
                }
            }, status=status.HTTP_200_OK)

        except razorpay.errors.BadRequestError as e:
            return Response({'error': 'Bad Request: {}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
           
