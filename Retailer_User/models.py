# models.py in the retailer app

from django.db import models
from User.models import CustomUser  # Adjust the import according to your structure

class Retailer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gst_no = models.CharField(max_length=15, blank=True, null=True)
    organization = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.organization or self.user.username
