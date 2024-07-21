import pyotp
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import *
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .tasks import send_email
from django.shortcuts import get_object_or_404
# Create your views here.

class RegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        print(email, password, "arrived")
        user = User.objects.filter(email=email)
        if user:
            print("user exists")
            return Response(
                {"message": "Email is already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = pyotp.TOTP(pyotp.random_base32()).now()

        print(otp, "otp")

        subject = "Welcome to Medicare, This is the otp for your verification"
        message = f"Hello!\n\nThank you for signing up with MediCare. Your OTP for account verification   is: {otp}\n\nPlease use this OTP to complete your registration.\n\nIf you did not sign up for a MediCare account, please ignore this email.\n\nBest regards,\nThe MediCare Team"
        recipient_list = [email]

        send_email(subject, message,recipient_list)

        temp_id = f"{email}_{otp}"
        temp = Temp(temp_id=temp_id, email=email, password=password, otp=otp)
        temp.save()
        return Response({"temp_id": temp_id}, status=status.HTTP_200_OK)
    

    def patch(self,request):
        print('patch is incoming>>>>>>>>>>>>>>.')
        user_id = request.data.get("userId")
        print('data>>>>>',request.data)
        print('user_id>>>>>>',user_id)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error':'user not found'},status=status.HTTP_404_NOT_FOUND
            )
        user.is_active = not user.is_active
        user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



class VerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        otp = request.data.get("otp")
        temp_id = request.data.get("temp_id")

        print(f"Received verification request - OTP: {otp}, Temp ID: {temp_id}")

        try:
            temp_registration = Temp.objects.get(temp_id=temp_id)
            stored_otp = temp_registration.otp

            print(f"Found temp registration - Stored OTP: {stored_otp}")

            if otp == stored_otp:
                user = User.objects.create_user(
                    email=temp_registration.email, password=temp_registration.password
                )
                user.save()
                print(f"User created successfully: {user.email}")

                temp_registration.delete()
                print("Temp registration deleted")

                return Response({"message": "created"}, status=status.HTTP_201_CREATED)
            else:
                print("OTP mismatch")
                return Response(
                    {"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Temp.DoesNotExist:
            print(f"No Temp object found for temp_id: {temp_id}")
            return Response(
                {"message": "Invalid temporary ID"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Unexpected error in VerifyView: {str(e)}")
            return Response(
                {"message": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserLoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        print(email, password, "user login data")

        user = authenticate(email=email, password=password)
        print(user, "Check User::")
        if user:
            print("user data authentication")
            login(request, user)

            refresh = RefreshToken.for_user(user)

            role = (
                "doctor"
                if user.is_doctor
                else ("superuser" if user.is_superuser else "user")
            )

            refresh["role"] = role
            refresh["user"] = user.email
            user_details = UserSerializer(user)
            user_data = user_details.data
            data = {}
            data["role"] = role
            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)
            data["user"] = user_data

            if role == "doctor":
                print("checking for doctor login ")
                doctor = Doctor.objects.get(user=user)
                doctor_data = DoctorSerializer(doctor).data
                data["doctor"] = doctor_data
            print(data)
            return Response(data, status=status.HTTP_200_OK)

        else:
            try:
                print(email, "email")
                user = User.objects.get(email=email)
                print(user, "Check User")
                if user:
                    print(user, "exists")
                    return Response(
                        {"detail": "Check password"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                else:
                    print("user doesent exist")
                # If the email exists but the password is incorrect, return a custom message
                return Response(
                    {"detail": "Check password"}, status=status.HTTP_401_UNAUTHORIZED
                )
            except User.DoesNotExist:
                # If the email does not exist, return a generic error message
                return Response(
                    {"detail": "Invalid Email "},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            


class RegisterDoctorView(APIView):
    print('heheheheh')
    permission_classes = [IsAdminUser]

    def post(self, request):
        print("Received data:>>>>>>>>>>>>", request.data)
        print("User:>>>>>>>>>>>", request.user)
        print("Headers:>>>>>>>>>>>", request.headers)

        email = request.data.get("email")
        password = request.data.get("password")

        # want to send a mail to the doctor this password as a content for his first login

        serializer = DoctorUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        print("---------user creation success", user.email)
        print("---------user creation success")

        formData = request.data.copy()
        formData["user"] = user.id

        print("------------user id addded to form data ")

        doctor_serializer = DoctorSerializer(data=formData)
        doctor_serializer.is_valid(raise_exception=True)
        doctor_serializer.save()

        print("doctor creation success")

        subject = "Welcome to Medicare, This is a confidential mail with password for your doctor login"
        message = password
        # from_mail = settings.EMAIL_HOST_USER
        to_mail = [email]
        # send_mail(subject, message, from_mail, to_mail)
        send_email(subject, message, to_mail)

        return Response(doctor_serializer.data, status=status.HTTP_201_CREATED)

    

class UsersManageView(APIView):

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def get(self,request, pk=None):
        users = User.objects.filter(Q(is_doctor=False) & Q(is_superuser=False) & Q(is_staff=False))
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def patch(self, request):
        location = request.data.get("location")
        profile_picture = request.data.get("profile_picture")

        current_password = request.data.get("currentPassword")
        new_password = request.data.get("newPassword")
        user_id = request.data.get("id")

        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Handle password update if both current and new passwords are provided
        if current_password and new_password:
            if not check_password(current_password, user.password):
                return Response({"message": "Invalid current password."},
                                status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({"message": "Password updated successfully."},
                            status=status.HTTP_200_OK)

        # Otherwise, update user profile data
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    

class DoctorListView(APIView):

    permission_classes=[IsAdminUser]

    def get(self,request):
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user(request):
    user_id = request.query_params.get("userId")
    user = get_object_or_404(User, id=user_id)
    serializer = UserSerializer(user).data
    
    return Response(serializer, status=status.HTTP_200_OK)


