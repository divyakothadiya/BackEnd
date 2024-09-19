# serializers.py
from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name', 'address',
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
        user.is_superuser = True  # Make the user a superuser
        user.is_staff = True  # Allow access to the admin panel
        user.save()
        return user
