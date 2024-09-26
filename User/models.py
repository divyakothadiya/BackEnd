from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    email = models.EmailField(
      verbose_name='Email',
      max_length=255,
      unique=True,
    )
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True, default='')
    phone_number = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{10}$')]
    )
    country = models.CharField(max_length=200, blank=True, null=True, default='')
    state = models.CharField(max_length=200, blank=True, null=True, default='')
    city = models.CharField(max_length=200, blank=True, null=True, default='')
    pincode = models.PositiveIntegerField(blank=True, null=True, default=0)
    profile_picture = models.TextField(blank=True, null=True, default='')
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, default='M')
    dob = models.DateField(blank=True, null=True)
    is_customer = models.BooleanField(default=False)
    is_retailer = models.BooleanField(default=False)
    otp = models.IntegerField(max_length=6,blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.email
