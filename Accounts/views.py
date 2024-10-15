import razorpay
from django.conf import settings
from rest_framework import status, views
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from .models import Invoice, Payment, User
from .serializers import InvoiceSerializer, PaymentSerializer
from rest_framework.views import APIView
from decimal import Decimal


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


class InvoiceCreateView(views.APIView):
    def post(self, request):
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            invoice = serializer.save()
            invoice.remaining_amount = invoice.price 
            invoice.save()

            response_data = {
                "invoice_id": invoice.id,
                "remaining_amount": invoice.remaining_amount
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PaymentView(views.APIView):
    def post(self, request):
        invoice_id = request.data.get('invoice_id')
        amount_paying = request.data.get('amount')
        payment_type = request.data.get('payment_type')  

        if not invoice_id or not amount_paying or not payment_type:
            return Response({"error": "invoice_id, amount, and payment_type are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount_paying = Decimal(request.data.get('amount'))


            if amount_paying <= 0:
                return Response({"error": "Amount must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

            invoice = Invoice.objects.get(id=invoice_id)
            invoice.payment_type = payment_type

            razorpay_order = razorpay_client.order.create({
                "amount": int(amount_paying * 100), 
                "currency": "INR",
                "payment_capture": "1"
            })

            payment = Payment.objects.create(
                invoice=invoice,
                order_id=razorpay_order['id'],
                amount=amount_paying,
            )

            if amount_paying > invoice.remaining_amount:
                return Response({'error':f"Amount should be less than the remaining balance - {invoice.remaining_amount}"})
            if payment_type == "full" and invoice.price != amount_paying:
                return Response({'error':f"Please ensure that you are paying the full amount if payment type is full - {invoice.price}"})

            if payment_type == 'partial':
                invoice.remaining_amount -= amount_paying 
            elif payment_type == 'full':
                invoice.remaining_amount = Decimal(0)  
            invoice.payment_type = payment_type
            invoice.amount_paying = amount_paying
            invoice.save()
            response_data = {
                "order_id": razorpay_order['id'],
                "amount": amount_paying,
            }

            if payment_type == 'partial':
                response_data["remaining_amount"] = invoice.remaining_amount
            
            invoice.order_id = response_data["order_id"]
            invoice.save()

            return Response(response_data, status=status.HTTP_200_OK)

        except Invoice.DoesNotExist:
            return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({"error": "Invalid amount value."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class VerifyPaymentView(views.APIView):
    def post(self, request):
        payment_id = request.data.get('payment_id')
        signature = request.data.get('signature')
        order_id = request.data.get('order_id') 
        invoice_id = request.data.get('invoice_id')

        try:
            payment = Payment.objects.get(order_id=order_id)
            invoice = Invoice.objects.get(id=invoice_id)

            try:
                razorpay_client.utility.verify_payment_signature({
                    'razorpay_order_id': order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature
                })
                
                if invoice.order_id != order_id:
                    return Response({'status':'Enter the correct invoice id for the Payment.'}) 

                if invoice.payment_type == 'partial':
                    invoice.payment_status = 'partially_paid' if invoice.remaining_amount > 0 else 'paid'
                elif invoice.payment_type == 'full':
                    invoice.payment_status = 'paid'
                invoice.save()   

                payment.sender = invoice.receiver
                payment.receiver = invoice.sender
                payment.price = invoice.price
                payment.remaining_amount = invoice.remaining_amount
                payment.payment_id = payment_id
                payment.signature = signature
                payment.save()

                return Response({"status": "Payment verified"}, status=status.HTTP_200_OK)

            except razorpay.errors.SignatureVerificationError:
                return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)

        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        


def payment_page(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        user = request.user 
    except Invoice.DoesNotExist:
        return render(request, '404.html', status=404)

   
    user_name = getattr(user, 'full_name', 'Guest')  
    user_email = getattr(user, 'email', 'guest@example.com') 
    user_contact = getattr(user, 'phone_number', '0000000000')  

    context = {
        'amount': invoice.amount_paying,
        'order_id': invoice.order_id,
        'user_name': user_name,
        'user_email': user_email,
        'user_contact': user_contact
    }

    return render(request, 'razorpay_payment.html', context)
