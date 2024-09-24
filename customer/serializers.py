from customer.models import User,OTP
from rest_framework import serializers
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)

    class Meta:

        model = User
        fields = ['id','email','password','confirm_password']


        def create(self, validated_data):

            if validated_data['password'] != validated_data.pop('confirm_password'):
                raise serializers.ValidationError({"password":"Password must match"})
            
            user = User(email=validated_data['email'])
            user.set_password(validated_data['password'])
            user.save()



            otp = OTP(user=user, expires_at=timezone.now() + timezone.timedelta(minutes=5))
            otp.save()  # Save the OTP to the database
            self.send_otp(user.email, otp.otp_code)  # Function to send OTP (you'll implement this)

            return user

            

    

        def send_otp(self, email, otp_code):

            send_mail(
                subject="One Time Password for Verification",
                message=f"Your OTP code is {otp_code}.it will expires in 5 minutes.",
                from_email="figmaproject886@gmail.com",
                recipient_list=[email],
                fail_silently=False,
            )

            # print(f"OTP {otp_code} send to email")
        
        def validate_email(self, value):

                if User.objects.filter(email=value).exists():
                    raise serializers.ValidationError("Email is already exists")
                return value






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



