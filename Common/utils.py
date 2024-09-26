from rest_framework.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives,EmailMessage
import random
from User.models import CustomUser
import os
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from django.utils import timezone




def check_empty_fields(data):
    for field, value in data.items():
        if not str(value):
            raise ValidationError({field: "This field may not be empty."})

def send_otp_via_email(request, email):
    # Generate a random OTP
    otp = random.randint(1000, 9999)

    # Define the context for rendering the email template
    context = {
        "otp": otp,
        "year": datetime.now().year
    }

    # Define the email subject and sender
    subject = 'Your customer account verification mail'
    email_from = os.environ.get('EMAIL_HOST_USER')

    try:
        
        html_content = render_to_string('email_otp.html', context, request=request)
        msg = EmailMultiAlternatives(subject, '', email_from, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        # Get the user object
        user_obj = CustomUser.objects.get(email=email)
        
        # Set OTP and expiry time
        user_obj.otp = otp
        user_obj.otp_expiry = datetime.now() + timedelta(minutes=30)  # Set expiry to 30 minutes from now
        user_obj.save()

        print({"message": f"OTP sent successfully: {otp}"})

    except Exception as e:
        print({"error": f"Error in sending email: {e}"})
      