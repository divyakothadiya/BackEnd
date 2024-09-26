from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegisterSerializer,UserLoginSerializer,UserProfileSerializer,VerifyUserSerializer
from .renderers import CustomUserRenderer
from Common.utils import check_empty_fields, send_otp_via_email
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from datetime import datetime
from Retailer_User.models import Retailer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegisterUserView(generics.CreateAPIView):
    renderer_classes = [CustomUserRenderer]
    permission_classes = [AllowAny] 
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        try:
            check_empty_fields(request.data)
            serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                    self.perform_create(serializer)
                    return Response({
                        'status': 200,
                        'message': 'Registration successfully done.',
                        'data': serializer.data,
                    })
            return Response({
                    'status': 400,
                    'message': 'Something went wrong',
                    'data': serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({
                'status': 406,
                'message': 'Validation error',
                'data': e.detail,
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'An error occurred',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginUserView(generics.CreateAPIView):
    renderer_classes = [CustomUserRenderer]
    permission_classes = [AllowAny] 
    serializer_class = UserLoginSerializer
    
    def post(self, request, format=None):
        try:
            check_empty_fields(request.data)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.data.get('email')
            password = serializer.data.get('password')

            try:
                user_obj = CustomUser.objects.get(email=email)
                username = user_obj.username
                # Get the username for authentication
            except CustomUser.DoesNotExist:
                return Response({'errors': {'non_field_errors': ['Invalid Email or Password']}}, status=status.HTTP_404_NOT_FOUND)

            # Authenticate the user using the username and password
            user = authenticate(request, username=username, password=password)
            if user is not None:
                is_customer = serializer.data.get('is_customer', False)
                is_retailer = serializer.data.get('is_retailer', False)
                if is_retailer:
                    # If trying to log in as a retailer
                    if user_obj.is_retailer:
                        # Include retailer details in the response
                        retailer_data = self.get_retailer_details(user=user)
                        return self.create_response(user=user, retailer_data=retailer_data)
                    elif user_obj.is_customer and not user_obj.is_retailer:
                        send_otp_via_email(request, email)
                        return Response({
                            'status': 'verification_needed',
                            'message': "You need to verify your account as a retailer. An OTP has been sent to your email.",
                            'data': serializer.data,
                        }, status=status.HTTP_403_FORBIDDEN)
                elif is_customer:
                    # Customer login logic
                    if user_obj.is_customer:
                        print("is_customer",user_obj)
                        return self.create_response(user=user)
                    elif user_obj.is_retailer and not user_obj.is_customer:
                        # Send OTP for customer verification
                        send_otp_via_email(request, email)
                        return Response({
                            'status': 'verification_needed',
                            'message': "You need to verify your account as a customer. An OTP has been sent to your email.",
                            'data': serializer.data,
                        }, status=status.HTTP_403_FORBIDDEN)
            
            else:
                return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({
                'status': 406,
                'message': 'Validation error',
                'data': e.detail,
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'An error occurred',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_response(self, user, retailer_data=None):
            required_fields = ['username', 'email', 'first_name', 'last_name', 'address', 'phone_number', 'country', 'state', 'city', 'pincode', 'profile_picture', 'gender', 'dob', 'is_customer', 'is_retailer']
            print("create_response",user)
            incomplete_profile = {}
            for field in required_fields:
                value = getattr(user, field, None)
                if value in [None, '', 'null']:
                    incomplete_profile[field] = value
            
            is_profile_complete_flag = len(incomplete_profile) == 0

            token = get_tokens_for_user(user)

            profile_data = UserProfileSerializer(user).data if user else {}

            if retailer_data:
                profile_data['retailer'] = retailer_data

            response_data = {
                'token': token,
                'msg': 'Login Success',
                'is_profile_complete': is_profile_complete_flag,
                'profile': profile_data,
                'incomplete_profile': incomplete_profile,
            }

            
            return Response(response_data, status=status.HTTP_200_OK)

    # Method to fetch retailer details
    def get_retailer_details(self, user):
            retailer = Retailer.objects.filter(user=user).first()
            try:
                retailer = Retailer.objects.filter(user=user).first()
                if retailer is not None:
                    retailer_data = {
                        'gst_no': retailer.gst_no,
                        'organization': retailer.organization,
                    }
                else:
                    retailer_data = {
                        'gst_no': '',
                        'organization': '',
                    }
            except retailer.DoesNotExist:
                retailer_data = None
            
            return retailer_data


class ProfileUserView(generics.RetrieveAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get(self, request, *args, **kwargs):
        
        try:
            profile = request.user
            serializer = self.get_serializer(profile)
            
            return Response({
                'status': status.HTTP_200_OK,
                'message': 'User profile retrieved successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'User profile not found.',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An error occurred.',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileUserUpdateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # Adding JSONParser
    serializer_class = UserProfileSerializer

    def put(self, request, format=None):
        try:
            profile, created = CustomUser.objects.get_or_create(email=request.user)
            print(profile)
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 200,
                    'message': 'Profile updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 400,
                'message': 'Something went wrong',
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'An error occurred',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteUserView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def delete(self, request, *args, **kwargs):
        try:
            user = request.user
            user.delete()
            return Response({
                'status': 200,
                'message': 'User deleted successfully',
                'data': {}
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'An error occurred',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class VerifyOTP(generics.CreateAPIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        try:
            check_empty_fields(request.data)
            serializer = VerifyUserSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.data['email']
                otp = serializer.data['otp']
                user = CustomUser.objects.filter(email=email).first()

                if not user:
                    return Response({
                        'status': 400,
                        'message': 'Something went wrong',
                        'data': 'Invalid user',
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if user.otp != otp:
                    print(user.otp)
                    print(otp)
                    return Response({
                        'status': 400,
                        'message': 'Something went wrong',
                        'data': 'Invalid OTP',
                    }, status=status.HTTP_400_BAD_REQUEST)

                if 'is_retailer' in request.data and request.data['is_retailer']:
                    print('retailer')
                    user.is_retailer = True
                    message = 'User verified and registered as retailer successfully.'
                else:
                    user.is_customer = True
                    message = 'User verified and registered as customer successfully.'

                user.otp = None  
                user.otp_expiry = None 
                user.save()

                return Response({
                    'status': 200,
                    'message': message,
                    'data': {'msg': message},
                })
            return Response({
                'status': 400,
                'message': 'Something went wrong',
                'data': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'An error occurred',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
