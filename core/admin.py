from django.contrib import admin
from .models import User, MediaFile, Purchase

admin.site.register(User)
admin.site.register(MediaFile)
admin.site.register(Purchase)
