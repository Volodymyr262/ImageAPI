from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# User's account tier
class accountTier(models.Model):
    name = models.CharField(max_length=50)
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    original_image = models.BooleanField(null=True)
    exp_link = models.BooleanField(null=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    account_tier = models.ForeignKey(accountTier, on_delete=models.SET_NULL, null=True)
    REQUIRED_FIELDS = ['email']


# image model that contains 2 thumbnails for standard account tiers and thumbnail field that contains
# custom thumbnail for custom account tiers
class ImageModel(models.Model):
    file = models.ImageField(upload_to='images/')
    file200px = models.ImageField(null=True, upload_to='images/')
    file400px = models.ImageField(null=True, upload_to='images/')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    thumbnail = models.ImageField(null=True, upload_to='images/')
    def image_url(self):
        return self.file.url


# temporary link model for expiring links to the images
class TemporaryLink(models.Model):
    file = models.ImageField(upload_to='images/', null=True)
    expiration_time = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    time = models.IntegerField(
        null=True,
        help_text="Number of seconds the link should expire in (between 300 and 30000).",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() >= self.expiration_time

    def image_url(self):
        return str(self.file)