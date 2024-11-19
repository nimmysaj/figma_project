# from django.shortcuts import render
# from Accounts.models import *

# # Create your views here.
# class RazorpayPaymentView(APIView):

#     @staticmethod
#     def create_razorpay_order(invoice):
#         client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
#         data = {
#             "amount": int(invoice.total_amount * 100),  # Amount in paise
#             "currency": "INR",
#             "receipt": f"invoice_{invoice.id}"
#         }
#         return client.order.create(data=data)

#     def post(self, request, *args, **kwargs):
#         # Retrieve the invoice ID and fetch the associated invoice object
#         invoice_id = request.data.get('invoice_id')
#         invoice = get_object_or_404(Invoice, id=invoice_id)

#         # Create a Razorpay order
#         try:
#             order = self.create_razorpay_order(invoice)
#         except Exception as e:
#             return Response({"error": f"Failed to create Razorpay order: {str(e)}"}, status=500)

#         # Attempt to create the Payment record
#         try:
#             payment = Payment.objects.create(
#                 invoice=invoice,
#                 order_id=order['id'],
#                 sender=invoice.sender,
#                 receiver=invoice.receiver,
#                 amount_paid=invoice.total_amount,
#                 payment_status="pending"
#             )
#             print("Payment created:", payment)  # Debugging line

#             return Response({
#                 "order_id": order['id'],
#                 "amount": order['amount'],
#                 "currency": order['currency']
#             })

#         except Exception as e:
#             # Log any errors and return a response
#             print("Error creating payment:", e)  # Debugging line
#             return Response({"error": f"Failed to create Payment: {str(e)}"}, status=500)
