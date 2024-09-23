from django.db import models

class Product(models.Model):
    category = models.CharField(max_length=255, null=False)  # category cannot be null
    product = models.JSONField(default=dict, null=True)  # product can be null, default to an empty JSON object

    def __str__(self):
        return self.category
