from customer.models import User,OTP
from rest_framework import serializers
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User
        fields = ['id','username','email','password','phone_number','is_customer','is_service_provider']


    def create(self, validated_data):

        user=User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            is_customer=validated_data['is_customer'],
            is_service_provider=validated_data['is_service_provider'],
        )

        otp_instance=OTP.objects.create(user=user,expires_at=timezone.now() + timezone.timedelta(minutes=5))

        send_mail(

            subject="One Time Password for Verification",
            message=f"Your OTP code is {otp_instance.otp_code}. It will expire at {otp_instance.expires_at}.",
            from_email="figmaproject24@gmail.com",
            recipient_list=[user.email],

        )

        return user
    
class OTPSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(max_length=6, required=True)

    def validate(self,data):

        email = data.get('email')
        otp_code = data.get('otp_code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        otp_instance = OTP.objects.filter(user=user,otp_code=otp_code).first()

        if not otp_instance:
            raise serializers.ValidationError("Invalide OTP code")
        
        if otp_instance.is_expired():
            raise serializers.ValidationError("OTP has expired")
        
        otp_instance.delete()

        data['user'] = user
        return data
    
    def generate_jwt_token(self, user):

        refresh  = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }



