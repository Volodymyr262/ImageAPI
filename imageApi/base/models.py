from django.db import models
from django.contrib.auth.models import AbstractUser


class accountTier(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    account_tier = models.ForeignKey(accountTier, on_delete=models.CASCADE, null=True)
    REQUIRED_FIELDS = ['email']


class ImageModel(models.Model):
    file = models.ImageField(upload_to='images/')
    file200px = models.ImageField(null=True, upload_to='images/')
    file400px = models.ImageField(null=True, upload_to='images/')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    expiring_link_seconds = models.IntegerField(
        null=True,
        help_text="Number of seconds the link should expire in (between 300 and 30000).",
    )
    def image_url(self):
        return self.file.url






