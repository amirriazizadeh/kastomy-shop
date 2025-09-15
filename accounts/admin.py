from django.contrib import admin

# Register your models here.
from .models import CustomUser,Address

admin.site.register(CustomUser)
admin.site.register(Address)