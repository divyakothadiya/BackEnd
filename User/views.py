from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegisterSerializer,UserLoginSerializer,UserProfileSerializer
from .renderers import CustomUserRenderer
from .utils import check_empty_fields
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterUserView(generics.CreateAPIView):
    renderer_classes = [CustomUserRenderer]
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
            # Fetch the user by email
            try:
                user_obj = CustomUser.objects.get(email=email)
                username = user_obj.username
                # Get the username for authentication
            except CustomUser.DoesNotExist:
                return Response({'errors': {'non_field_errors': ['Invalid Email or Password']}}, status=status.HTTP_404_NOT_FOUND)

            # Authenticate the user using the username and password
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Check if user profile exists
                try:
                    user_profile = user_obj
                except CustomUser.DoesNotExist:
                    user_profile = None
                # Define required fields for profile completion
                required_fields = ['username', 'email', 'first_name', 'last_name', 'address', 'phone_number', 'country', 'state', 'city', 'pincode', 'profile_picture', 'gender']
                
                if user_profile:
                    incomplete_profile = {}
                    for field in required_fields:
                        value = getattr(user_profile, field, None)
                        if value in [None, '', 'null']:
                            incomplete_profile[field] = value
                    
                    is_profile_complete_flag = len(incomplete_profile) == 0

                    # Generate the token
                    token = get_tokens_for_user(user)

                    profile_data = UserProfileSerializer(user_profile).data if user_profile else {}
                    
                    return Response({
                        'token': token,
                        'msg': 'Login Success',
                        'is_profile_complete': is_profile_complete_flag,
                        'profile': profile_data,  # Profile data
                        'incomplete_profile': incomplete_profile,  # Incomplete fields
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'token': get_tokens_for_user(user),
                        'msg': 'Login Success',
                        'is_profile_complete': False,
                        'profile': {},  # Empty profile if user_profile is None
                        'incomplete_profile': required_fields,  # All required fields are incomplete
                    }, status=status.HTTP_200_OK)
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

# class UserProfileUpdateView(generics.CreateAPIView):
#     # permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]  # Adding JSONParser
    
#     def put(self, request, format=None):
#         try:
#             profile, created = CustomUser.objects.get_or_create(email=request.user)
#             print(profile)
#             serializer = UserProfileSerializer(profile, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({
#                     'status': 200,
#                     'message': 'Profile updated successfully',
#                     'data': serializer.data
#                 }, status=status.HTTP_200_OK)
            
#             return Response({
#                 'status': 400,
#                 'message': 'Something went wrong',
#                 'data': serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         except Exception as e:
#             return Response({
#                 'status': 500,
#                 'message': 'An error occurred',
#                 'data': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
