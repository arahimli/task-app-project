from django.contrib import admin
# from user_app.forms import MyUserChangeForm, MyUserCreationForm
# Register your models here.
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from user_app.forms import CustomUserChangeForm, CustomUserCreationForm

# User = get_user_model()

# Admin panel actions here
from user_app.models import CustomUser, UserConfrimationKeys


def make_verified_user(modeladmin, request, queryset):
    queryset.update(verified=True)


make_verified_user.short_description = "Confirm user"


class CustomUserAdmin(AuthUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal information'), {'fields': (
        'first_name', 'last_name', 'phone', 'usertype', 'profile_picture',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser','groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ("first_name", "last_name", 'username', 'password1', 'password2'),
        }),
    )
    # The forms to add and change user instances
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('username','email', 'first_name', 'last_name', 'is_staff',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'username', 'email')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)
    actions = [make_verified_user]


admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(UserConfrimationKeys)

# class UserPermissionAdmin(admin.ModelAdmin):
#     list_display = ['user','permission',]
# admin.site.register(UserPermission,UserPermissionAdmin)