from django.db import models

# Create your models here.


class accountTier(models.Model):
    name = models.CharField(max_length=50)


class Image(models.Model):
    title = models.CharField(null=True, max_length=100)
    file = models.ImageField(upload_to='images/')

    def image_url(self):
        return self.file.url