from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

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