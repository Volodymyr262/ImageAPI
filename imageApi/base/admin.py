from django.contrib import admin
from .models import ImageModel, accountTier, User, TemporaryLink

admin.site.register(ImageModel)
admin.site.register(accountTier)
admin.site.register(User)
admin.site.register(TemporaryLink)
