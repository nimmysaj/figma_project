from django.db import models

from django.conf import settings

class Invoice(models.Model):
    INVOICE_TYPE_CHOICES = [
        ('service_request', 'Service Request'),
        ('dealer_payment', 'Dealer Payment'),
        ('provider_payment', 'Service Provider Payment'),
    ]

    invoice_number = models.IntegerField(unique=True)  # Ensure unique invoice numbers
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES)
    # Sender (user who is paying) and receiver (user receiving payment)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sent_invoices')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='received_invoices')

    quantity = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid'), ('cancelled', 'Cancelled')], default='pending')

    invoice_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    appointment_date = models.DateTimeField()
    additional_requirements = models.TextField(null=True, blank=True)
    accepted_terms = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice #{self.invoice_number} from {self.sender} to {self.receiver} - {self.payment_status}"
    
    def mark_paid(self):
        """Method to mark the invoice as paid."""
        self.payment_status = 'paid'
        self.save()

    def cancel_invoice(self):
        """Method to cancel the invoice."""
        self.payment_status = 'cancelled'
        self.save()


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('razorpay', 'Razorpay'),
        # Add other payment methods if necessary
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sent_payments')  # User who sends the payment
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='received_payments')  # User who receives the payment
    transaction_id = models.CharField(max_length=15, blank=True, null=True)  # Optional: ID from the payment provider
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)  # Automatically set the date when the payment is created
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    # Fields for Razorpay confirmation
    payment_id = models.CharField(max_length=200, verbose_name="Payment ID", blank=True)
    order_id = models.CharField(max_length=200, verbose_name="Order ID")
    signature = models.CharField(max_length=500, verbose_name="Signature", blank=True, null=True)

    def __str__(self):
        return f"Payment of {self.amount_paid} by {self.sender} to {self.receiver} - {self.payment_status}"

    def mark_completed(self):
        self.payment_status = 'completed'
        self.save()

    def mark_failed(self):
        self.payment_status = 'failed'
        self.save()

