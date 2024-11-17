from django.shortcuts import render, redirect

# Create your views here.
import razorpay
from django.conf import settings
from Accounts.models import Invoice, Payment
import razorpay
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q




def create_payment_view(request):
    return render(request, 'create_payment.html')


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_payment_post(request):
    if request.method == 'POST':
        invoice_id = request.POST.get('invoice_id')

        if not invoice_id:
            return HttpResponse(
                "<script>alert('Please enter an invoice ID.'); window.history.back();</script>"
            )

        try:
            invoice = Invoice.objects.get(Q(id=invoice_id) & (Q(payment_status='pending') | Q(payment_status='partially paid')))
            amount = float(invoice.total_amount)  # Convert Decimal to float
            name = invoice.sender.full_name
            email = invoice.sender.email
            phone = invoice.sender.phone_number
            description = invoice.description
            # Create Razorpay order
            order = razorpay_client.order.create({
                'amount': amount * 100,  # Razorpay accepts amount in paise (1 INR = 100 paise)
                'currency': 'INR',
                'payment_capture': '1'
            })

            order_id = order['id']

            # Render the payment page with Razorpay order details
            return render(request, 'make_payment.html', {
                'invoice_id': invoice.id,
                'amount': amount,  # Send the amount as a float
                'order_id': order_id,
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'name':name,
                'email':email,
                'phone':phone,
                'description': description,
            })

        except Invoice.DoesNotExist:
            return HttpResponse(
                "<script>alert('Invoice with the provided ID does not exist or Payment Already Done !!'); window.history.back();</script>"
            )

    return redirect('create_payment_view')  # Redirect to the create payment page if the request is not POST


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        try:
            # Parse incoming data
            data = json.loads(request.body)
            transaction_id = data.get('transaction_id')
            order_id = data.get('order_id')
            signature = data.get('signature')
            invoice_id = data.get('invoice_id')
            amount_paid = float(data.get('amount_paid')) 
            # Verify Razorpay signature
            try:
                generated_signature = razorpay_client.utility.verify_payment_signature({
                    'razorpay_order_id': order_id,
                    'razorpay_payment_id': transaction_id,
                    'razorpay_signature': signature
                })
                
                # If signature is valid, process the payment
                if generated_signature:
                    try:
                        # Get the invoice and associated sender/receiver
                        invoice = Invoice.objects.get(id=invoice_id)
                        sender = invoice.sender
                        receiver = invoice.receiver

                        # Create a new payment record
                        payment = Payment(
                            invoice=invoice,
                            sender=sender,
                            receiver=receiver,
                            transaction_id=transaction_id,
                            order_id=order_id,
                            signature=signature,
                            amount_paid=amount_paid,  # Store as float or Decimal
                            payment_status='completed',
                        )
                        payment.save()

                        # Update the invoice status
                        invoice.payment_status = 'paid'
                        invoice.save()

                        return JsonResponse({'status': 'success'})

                    except Invoice.DoesNotExist:
                        # Invoice not found
                        payment = Payment(
                            invoice_id=invoice_id,
                            transaction_id=transaction_id,
                            order_id=order_id,
                            signature=signature,
                            amount_paid=amount_paid,
                            payment_status='failed'
                        )
                        payment.save()
                        return JsonResponse({'status': 'failure', 'message': 'Invoice not found'}, status=404)

                else:
                    # Signature verification failed
                    payment = Payment(
                        invoice_id=invoice_id,
                        transaction_id=transaction_id,
                        order_id=order_id,
                        signature=signature,
                        amount_paid=amount_paid,
                        payment_status='failed'
                    )
                    payment.save()

                    return JsonResponse({'status': 'failure', 'message': 'Signature verification failed'}, status=400)

            except razorpay.errors.SignatureVerificationError as e:
                # Handle signature verification errors from Razorpay
                payment = Payment(
                    invoice_id=invoice_id,
                    transaction_id=transaction_id,
                    order_id=order_id,
                    signature=signature,
                    amount_paid=amount_paid,
                    payment_status='failed'
                )
                payment.save()

                return JsonResponse({'status': 'failure', 'message': str(e)}, status=400)

        except json.JSONDecodeError:
            # Handle case if the request body is not valid JSON
            return JsonResponse({'status': 'failure', 'message': 'Invalid JSON format'}, status=400)

        except Exception as e:
            # Catch any unexpected errors during payment processing
            payment = Payment(
                invoice_id=invoice_id,
                transaction_id=transaction_id,
                order_id=order_id,
                signature=signature,
                amount_paid=amount_paid,
                payment_status='failed'
            )
            payment.save()

            return JsonResponse({'status': 'failure', 'message': str(e)}, status=500)

    # If the request method is not POST
    return JsonResponse({'status': 'failure', 'message': 'Invalid request method'}, status=400)
        
def payment_success(request):
    return render(request, 'payment_success.html')