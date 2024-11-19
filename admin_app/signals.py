from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from Accounts.models import Invoice
from .models import IncomeManagement, AccountDetails
from decimal import InvalidOperation

@receiver(post_save,sender=Invoice)
def calculate_amount_balance(sender,instance,created,*args,**kwargs): 
    #if created and instance.service_register: 
    #    print('hi',flush=True)  

    if created:
        print(instance.invoice_type)
        income = IncomeManagement.objects.filter(income_type = instance.invoice_type).first()
        split_type = income.split_type 

        total_invoice_amount = instance.price
        reciever =  instance.receiver 

        if instance.payment_status == "paid" :

            try:
                total_invoice_amount = instance.price # Ensure it's a valid Decimal
                income = IncomeManagement.objects.filter(income_type=instance.invoice_type).first()
                if not income:
                    return  # No income type found, exit gracefully

                if income.company > 0:
                    if income.split_type == "Percentage":
                        amount = (total_invoice_amount * income.company) / 100
                    else:
                        amount = income.company

                    # Handle receiver's account
                    user = AccountDetails.objects.filter(user_id=instance.receiver).first()
                    if user:
                        user.account_balance += amount
                        user.save()
                    else:
                        AccountDetails.objects.create(user_id=instance.receiver, account_balance=Decimal(amount))
            except (InvalidOperation, TypeError, ValueError) as e:
                print(f"Error in calculate_amount_balance: {e}")

            if instance.service_register:

                franchise_id = instance.service_register.service_provider.franchisee.user
                dealer_id =  instance.service_register.service_provider.dealer.user
                service_provider = instance.service_register.service_provider.user 
                
                if franchise_id:
                    if split_type == "Percentage":
                        amount = (total_invoice_amount * income.franchisee) / 100
                    else:
                        amount = income.franchisee 

                    user = AccountDetails.objects.filter(user_id=franchise_id).first()
                    if user:
                        user.account_balance += amount 
                        user.save()
                    else:
                        user = AccountDetails.objects.create(user_id=franchise_id,account_balance=amount)

                if dealer_id:
                    if split_type == "Percentage":
                        amount = (total_invoice_amount * income.dealer) / 100
                    else:
                        amount = income.dealer 

                    user = AccountDetails.objects.filter(user_id=dealer_id).first()
                    if user:
                        user.account_balance += amount 
                        user.save()
                    else:
                        user = AccountDetails.objects.create(user_id=dealer_id,account_balance=amount)

                if service_provider:
                    if split_type == "Percentage":
                        amount = (total_invoice_amount * income.service_provider) / 100
                    else:
                        amount = income.service_provider 

                    user = AccountDetails.objects.filter(user_id=service_provider).first()
                    if user:
                        user.account_balance += amount 
                        user.save()
                    else:
                        user = AccountDetails.objects.create(user_id=service_provider,account_balance=amount)
    else:
        None 