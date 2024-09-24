from rest_framework import serializers
from .models import CustomUser
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re

class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', "password2", 'first_name', 'last_name', 'address',
            'phone_number', 'country', 'state', 'city', 'pincode', 'profile_picture',
            'gender', 'dob'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'address': {'required': False},
            'phone_number': {'required': False},
            'country': {'required': False},
            'state': {'required': False},
            'city': {'required': False},
            'pincode': {'required': False},
            'profile_picture': {'required': False},
            'gender': {'required': False},
            'dob': {'required': False}
        }
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match")
        return attrs

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format.")
        
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Email format is invalid. Domain must not contain numbers.")

        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        
        return value

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            address=validated_data.get('address', ''),
            phone_number=validated_data.get('phone_number', ''),
            country=validated_data.get('country', ''),
            state=validated_data.get('state', ''),
            city=validated_data.get('city', ''),
            pincode=validated_data.get('pincode', 0),
            profile_picture=validated_data.get('profile_picture', ''),
            gender=validated_data.get('gender', 'M'),
            dob=validated_data.get('dob', None),
        )
        user.set_password(validated_data['password'])
        user.is_superuser = True
        user.is_staff = True  # Allow access to the admin panel
        user.save()
        return user
    
class UserLoginSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    model = CustomUser
    fields = ['email', 'password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'address', 'phone_number', 'country', 'state', 'city', 'pincode', 'profile_picture', 'gender', 'dob']
