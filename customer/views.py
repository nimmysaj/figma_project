from rest_framework import generics, permissions, status
from rest_framework.response import Response
from Accounts.models import User, OTP
from .serializers import UserRegistrationSerializer


class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')

        # Ensure either email or phone number is provided, but not both
        if (phone_number and email) or (not phone_number and not email):
            return Response(
                {"message": "Please provide either an email or a phone number, not both."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for email registration
        if email:
            # Using email registration logic
            serializer = UserRegistrationSerializer(data=request.data)
            if User.objects.filter(email=email).exists():
                return Response({"message": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        elif phone_number:
            # Using phone registration logic
            serializer = UserRegistrationSerializer(data=request.data)
            if User.objects.filter(phone_number=phone_number).exists():
                return Response({"message": "Phone number already exists."}, status=status.HTTP_400_BAD_REQUEST)

        
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        
        if email:
            return Response(
                {"message": "User registered successfully. Please check your email for OTP."},
                status=status.HTTP_201_CREATED
            )
        elif phone_number:
            return Response(
                {"message": "User registered successfully. Please check your phone for OTP."},
                status=status.HTTP_201_CREATED
            )



from rest_framework import generics, permissions, status
from rest_framework.response import Response
from Accounts.models import User, OTP
from .serializers import OTPSerializer

class OTPVerificationView(generics.GenericAPIView):
    serializer_class = OTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        
        user = serializer.validated_data['user']
        
        return Response({
            "message": "OTP verified successfully. Registration completed."
        }, status=status.HTTP_200_OK)


# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response

# class UserProfileView(APIView):
#     permission_classes = [IsAuthenticated]  # Ensures only authenticated users can access

#     def get(self, request):
#         print(f"Request User: {request.user}")
#         user = request.user  # Get the current logged-in user
        
#         # Prepare the response data
#         return Response ({
#             'email': user.email if user.email else None,  # Return email if exists
#             'phone_number': user.phone_number if user.phone_number else None,  # Return phone number if exists
#             'is_customer': user.is_customer,  
#             'is_service_provider': user.is_service_provider,
#         })

#         # return Response(response_data)



