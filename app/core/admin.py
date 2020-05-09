from django.contrib import admin

# Register your models here.
from core.models import UserLoginLog

admin.site.register(UserLoginLog)