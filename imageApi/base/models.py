from django.db import models

# Create your models here.


class accountTier(models.Model):
    name = models.CharField(max_length=50)


class Image(models.Model):
    file = models.ImageField(upload_to='images/')