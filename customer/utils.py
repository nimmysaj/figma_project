from Accounts.models import OTP
from figma import settings
from django.utils import timezone
import random
from django.core.mail import send_mail
# from twilio.rest import Client

def send_otp_via_email(user):
    # Save OTP in the database (model will handle OTP code generation and expiration)
    otp = OTP.objects.create(user=user)

    # Send OTP via email
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp.otp_code}. It will expire in 5 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)

    return otp


def send_otp_via_sms(user, otp_code):
    # Get the Twilio client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    # Craft the message content
    message_body = f'Your OTP code is {otp_code}. It will expire in 5 minutes.'

    # Send SMS using Twilio's API
    message = client.messages.create(
        body=message_body,
        from_=settings.TWILIO_PHONE_NUMBER,  # Twilio verified phone number
        to=user.phone_number  # The user's phone number
    )

    return message.sid  # Return message SID for tracking


def send_otp_via_phone(user):
    otp = OTP.objects.create(user=user)
    
    # Send OTP via SMS
  #  send_otp_via_sms(user, otp.otp_code)  # Implemented earlier
    print(otp.otp_code)
    return otp

