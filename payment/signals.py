from django.db.models.signals import post_save
from django.dispatch import receiver
from Accounts.models import Payment, User ,Invoice ,Franchisee

@receiver(post_save, sender=Invoice)
def update_franchisee_status(sender, instance, created, **kwargs):
    if instance.payment_status == 'paid' and instance.payment_balance == 0:
        # Check if the invoice type is 'franchisee_registration'
        if instance.invoice_type == 'franchisee_registration':
            try:
                # Assuming franchisee is linked to the invoice's sender (User)
                user_id = instance.sender
                # Check if `sender` is a User and then get the associated Franchisee
                franchisee = Franchisee.objects.get(user=user_id)
                # Log the user_id for debugging
                print(f"Franchisee linked to User ID: {user_id}")
                # Change franchisee status to 'active'
                franchisee.status = 'Active'
                franchisee.save()
                print(f"Franchisee {franchisee.id} status updated to active.")
            except Franchisee.DoesNotExist:
                # Handle case where no franchisee is linked to the sender
                print(f"No Franchisee found for User ID: {user_id}")
            except AttributeError:
                # Handle case where there is an issue with the sender's user
                print("Error with the sender's user object.")
    else:
        print("Invoice is either not paid or not a franchisee registration.")
