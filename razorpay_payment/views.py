from django.shortcuts import render
import razorpay_payment
import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from Accounts.models import Invoice,Payment
from django.utils import timezone

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=('key_id', 'secret_key'))
key_id ="rzp_test_FbCOh14w74Nyzy"
secret_key="wpO4uHIeuiEQ24mdTffEVO8p"

def Razorpay_Payment(request):
    print("workkasdfassssfasfasfa")

    if request.method == "POST":
        razorpay_client = razorpay.Client(auth=('rzp_test_FbCOh14w74Nyzy', 'wpO4uHIeuiEQ24mdTffEVO8p'))
        invoice_id = request.POST.get("invoice_id")
    
        # Fetch the invoice from the database
        invoice = get_object_or_404(Invoice, invoice_number=invoice_id)

        # Check if the invoice is already paid
        if invoice.payment_status == 'paid':
            return JsonResponse({"error": "This invoice is already paid."}, status=400)

        # Create Razorpay order
        amount = int(invoice.price * 100)  # Convert to paise (smallest currency unit)
        order_data = {
            "amount": amount,
            "currency": "INR",
            "receipt": f"invoice_{invoice_id}",
            "payment_capture": 1,  # Auto-capture the payment
        }
        razorpay_order = razorpay_client.order.create(order_data)

        # Pass Razorpay order details to the template
        context = {
            "invoice": invoice,
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key_id": key_id,
            "amount": amount,
        }
        return render(request, "payment.html", context)

    return render(request, "payment_form.html")
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def razorpay_success(request):
    if request.method == "POST":
        data = json.loads(request.body)
        invoice_id = data.get("invoice_id")
        payment_id = data.get("razorpay_payment_id")
        order_id = data.get("razorpay_order_id")
        signature = data.get("razorpay_signature")

        try:
            # Update the invoice status to 'paid'
            invoice = Invoice.objects.get(invoice_number=invoice_id)
            invoice.payment_status = 'paid'
            invoice.save()

            # Create a new Payment record
            Payment.objects.create(
                invoice=invoice,
                sender=invoice.sender,
                receiver=invoice.receiver,
                transaction_id=payment_id,
                order_id=order_id,
                signature=signature,
                amount_paid=invoice.price,
                payment_method='razorpay',
                payment_date=timezone.now(),
                payment_status='completed'
            )

            return JsonResponse({"success": True})
        except Invoice.DoesNotExist:
            return JsonResponse({"error": "Invoice not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)
