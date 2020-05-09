from django.contrib import admin

# Register your models here.
from content.models import SharedFile, SharedFileUser, Comment

admin.site.register(SharedFile)
admin.site.register(SharedFileUser)
admin.site.register(Comment)