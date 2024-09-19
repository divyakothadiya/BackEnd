# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 'address',
            'phone_number', 'country', 'state', 'city', 'pincode',
            'profile_picture', 'gender', 'dob'
        ]
