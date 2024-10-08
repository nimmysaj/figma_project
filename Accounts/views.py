from rest_framework import viewsets, status 
from rest_framework.response import Response
from .models import Invoice, Payment
from .serializers import InvoiceSerializer
import razorpay
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import render



class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()
        
        return Response({'invoice_id': invoice.id}, status=status.HTTP_201_CREATED)



class PaymentInitiationView(APIView):
    def post(self, request):
        invoice_id = request.data.get('invoice_id')

        if not invoice_id:
            return Response({"error": "Invoice ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice = Invoice.objects.get(id=invoice_id)

            if invoice.payment_status != 'pending':
                return Response({"error": "Invoice cannot be paid."}, status=status.HTTP_400_BAD_REQUEST)

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))


            order_amount = int(invoice.total_amount * 100)  
            order_currency = 'INR'
            order_receipt = f"receipt#_{invoice.id}"
            order = client.order.create({
                'amount': order_amount,
                'currency': order_currency,
                'receipt': order_receipt,
                'payment_capture': 1, 
            })

            payment = Payment.objects.create(
                invoice=invoice,
                sender=invoice.sender,
                receiver=invoice.receiver,
                amount_paid=invoice.total_amount,
                payment_method='razorpay',
                payment_date=request.data.get('payment_date', None), 
                payment_status='pending',
                payment_id=order['id'],  
                order_id=order['id'],  
            )

            return Response({
                "message": "Payment initiated successfully.",
                "order_id": order['id'],  
                "amount": order_amount,
                "currency": order_currency,
            }, status=status.HTTP_201_CREATED)

        except Invoice.DoesNotExist:
            return Response({"error": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class PaymentConfirmationView(APIView):
    def post(self, request):
        order_id = request.data.get('order_id')
        payment_id = request.data.get('payment_id')  
        signature = request.data.get('signature')  

        if not order_id or not payment_id or not signature:
            return Response({"error": "order_id, payment_id, and signature are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(order_id=order_id)

            payment.transaction_id = payment_id
            payment.signature = signature

            is_success = True  

            if is_success:
                payment.mark_completed()

                invoice = payment.invoice
                invoice.mark_paid()

                success_message = "Your payment has been processed successfully."
                payment_status = "completed"
                invoice_status = "paid"

                return Response({
                    'success_message': success_message,
                    'order_id': order_id,
                    'payment_id': payment_id,
                    'signature': signature,
                    'payment_status': payment_status,
                    'invoice_status': invoice_status
                }, status=status.HTTP_200_OK)
            else:
                payment.mark_failed()
                return Response({"message": "Payment failed.", "payment_status": "failed"}, status=status.HTTP_400_BAD_REQUEST)

        except Payment.DoesNotExist:
            return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




def razorpay_payment_page(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)

        if invoice.payment_status != 'pending':
            return render(request, 'razorpay_payment.html', {
                'message': 'Invoice cannot be paid.'
            })

        if request.user.is_authenticated:
            user_name = request.user.get_full_name()
            user_email = request.user.email
        else:
            user_name = "Guest" 
            user_email = "" 

        payment = invoice.payments.first()  

        order_id = payment.order_id if payment else None

        context = {
            'order_id': order_id,
            'amount': int(invoice.total_amount * 100),  
            'user_name': user_name,
            'user_email': user_email,
            'razorpay_key': settings.RAZORPAY_KEY_ID  
        }

        return render(request, 'razorpay_payment.html', context)

    except Invoice.DoesNotExist:
        return render(request, 'razorpay_payment.html', {
            'message': 'Invoice not found.'
        })


