from django.db import models

# Create your models here.
class Credit_Card(models.Model):
    category=models.CharField(max_length=500)
    amount=models.CharField(max_length=500)
    latitude=models.CharField(max_length=500)
    longitude=models.CharField(max_length=500)
    merchant_latitude=models.CharField(max_length=500)
    merchant_longitude=models.CharField(max_length=500)
    jobs=models.CharField(max_length=500)
    prediction=models.CharField(max_length=500)