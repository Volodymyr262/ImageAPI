from django.contrib import admin
from .models import ImageModel, accountTier, User

admin.site.register(ImageModel)
admin.site.register(accountTier)
admin.site.register(User)
