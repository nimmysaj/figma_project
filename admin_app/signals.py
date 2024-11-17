from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from Accounts.models import Invoice
from .models import IncomeManagement, AccountDetails


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

        if instance.payment_status == "pending" :

            if income.company > 0:
                if split_type == "Percentage":
                    amount = (total_invoice_amount * income.company) / 100
                else:
                    amount = income.company 

                user = AccountDetails.objects.filter(user_id = reciever).first()
                if user:  
                    user.account_balance += amount 
                    user.save()
                else:
                    user = AccountDetails.objects.create(user_id = reciever, account_balance = amount)

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