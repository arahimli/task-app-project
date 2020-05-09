import os
# from nocaptcha_recaptcha.fields import NoReCaptchaField
from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from django.contrib.auth import authenticate
User = get_user_model()
from PIL import Image
GUser = get_user_model()



class CustomUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput(attrs={'autocomplete': 'off','placeholder': _("Password"),}))
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput(attrs={'autocomplete': 'off','placeholder': _("Password confirmation"),}),
                                help_text=_("Enter the same password as above, for verification."))

    first_name = forms.CharField(label=_("First name"),
                                widget=forms.TextInput(attrs={'autocomplete': 'off','placeholder': _("First name"),}),
                                help_text=_("First name"))
    last_name = forms.CharField(label=_("Last name"),
                                widget=forms.TextInput(attrs={'autocomplete': 'off','placeholder': _("Last name"),}),
                                help_text=_("Last name"))

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': _("Username") }),
            'email': forms.TextInput(attrs={'placeholder': _("Email") }),
            'first_name': forms.TextInput(attrs={'placeholder': _("First name") }),
            'last_name': forms.TextInput(attrs={'placeholder': _("Last name") }),
        }
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):


    first_name = forms.CharField(label=_("First name"),
                                widget=forms.TextInput(attrs={'autocomplete': 'off','placeholder': _("First name"),}),
                                help_text=_("First name"))
    last_name = forms.CharField(label=_("Last name"),
                                widget=forms.TextInput(attrs={'autocomplete': 'off','placeholder': _("Last name"),}),
                                help_text=_("Last name"))


    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_(
                                             "Raw passwords are not stored in the database, they can not be seen at all "
                                             "this is the user's password, but you can change it "
                                             " <a href=\"../password/\">this form</a>. by"))



    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]



class CustomUserChangeResForm(forms.ModelForm):


    first_name = forms.CharField(label=_("First name"),
                                widget=forms.TextInput(attrs={'autocomplete': 'off','placeholder': _("First name"),}),
                                help_text=_("First name"))
    last_name = forms.CharField(label=_("Last name"),
                                widget=forms.TextInput(attrs={'autocomplete': 'off','placeholder': _("Last name"),}),
                                help_text=_("Last name"))


    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_(
                                             "Raw passwords are not stored in the database, they can not be seen at all "
                                             "this is the user's password, but you can change it "
                                             " <a href=\"../password/\">this form</a>. by"))



    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name',)

        widgets = {
            'username': forms.TextInput(attrs={'placeholder': _('Username')}),
            'email': forms.TextInput(attrs={'placeholder': _('Email address')})
        }
    def __init__(self, *args, **kwargs):
        super(CustomUserChangeResForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
