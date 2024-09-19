from rest_framework.exceptions import ValidationError
def check_empty_fields(data):
    for field, value in data.items():
        if not str(value):
            raise ValidationError({field: "This field may not be empty."})
        
def is_profile_complete(user_profile):
    # Define the required fields in the UserProfile
    required_fields = ['first_name', 'last_name', 'phone_number', 'address', 'country', 'state', 'city', 'pincode']
    
    # Check if any required field is missing or empty
    for field in required_fields:
        value = getattr(user_profile, field, None)
        if not value:  # Field is missing or empty
            return False
    
    # Profile is complete
    return True
