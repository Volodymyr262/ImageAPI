from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class accountTier(models.Model):
    name = models.CharField(max_length=50)


class ImageModel(models.Model):
    title = models.CharField(null=True, max_length=100)
    file = models.ImageField(upload_to='images/')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def image_url(self):
        return self.file.url


