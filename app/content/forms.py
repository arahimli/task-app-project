import datetime

import pytz
from django import forms
from django.utils.translation import ugettext_lazy as _

from content.models import SharedFile, SharedFileUser, Comment
from core._tools.choices import ORDERTYPE_CHOICE, SHAREDFILEMODEL_CHOICES, FILETYPES_CHOICES


class SharedFileForm(forms.ModelForm):

    title = forms.CharField(required=True,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': _("Title") }))
    description = forms.CharField(required=True,widget=forms.Textarea(attrs={'class': 'form-control','placeholder': _("Description") }))

    expiration_date = forms.DateTimeField(required=True,input_formats=('%d.%m.%Y %H:%M',),widget=forms.DateTimeInput(format='%d.%m.%Y %H:%M',
        attrs={'placeholder': _('Expiration date'), 'autocomplete': 'off',
               'class': 'form-control', }))
    class Meta:
        model = SharedFile
        fields = ('title', 'description', 'expiration_date',)

    def clean(self):

        cleaned_data = super(SharedFileForm, self).clean()
        errors = []
        utc = pytz.UTC
        expiration_date = cleaned_data['expiration_date']
        print(expiration_date)
        print(utc.localize(datetime.datetime.now() + datetime.timedelta(minutes=30)) )
        # Test 1
        if expiration_date <= utc.localize(datetime.datetime.now() + datetime.timedelta(hours=5)):
            self.add_error('expiration_date', _('Expiration date have to be 5 hours more than today'))

        #     errors.append(forms.ValidationError(_('Expiration date have to be one day more than today')))
        #
        # if errors:
        #     raise forms.ValidationError(errors)

        return cleaned_data


class SharedFileOnlyFileForm(forms.ModelForm):

    class Meta:
        model = SharedFile
        fields = ( 'file',)

class SharedFileUserForm(forms.ModelForm):
    class Meta:
        model = SharedFileUser
        fields = ['user', 'shared_file', 'permission_type']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text',]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control','placeholder': _("Title") }),
            'text': forms.Textarea(attrs={'class': 'form-control','placeholder': _("Comment"), 'rows':3 }),
        }


class FileSearchForm(forms.Form):
    search = forms.CharField(max_length=255,label=_('Search text'), required=False, widget=forms.TextInput(
        attrs={'placeholder': _('Search text...'), 'autocomplete': 'off',
               'class': 'form-control', }))
    field_list = forms.ChoiceField(choices=[],label=_('Field'),  required=True, widget=forms.Select(attrs={'placeholder': _('Field'), 'autocomplete': 'off','class': 'form-control', }))
    order_type = forms.ChoiceField(choices=ORDERTYPE_CHOICE ,label=_('Order'),  required=False, widget=forms.Select(attrs={'placeholder': _('Order'), 'autocomplete': 'off','class': 'form-control', }))

    start_date = forms.DateField(input_formats=('%d.%m.%Y',),label=_('Start date'), required=False,widget=forms.DateInput(format='%d.%m.%Y',attrs={'placeholder': _('Start date'), 'autocomplete': 'off','class': 'form-control', }))
    end_date = forms.DateField(input_formats=('%d.%m.%Y',),label=_('End date'), required=False,widget=forms.DateInput(format='%d.%m.%Y',attrs={'placeholder': _('End date'), 'autocomplete': 'off','class': 'form-control', }))
    def __init__(self, field_list_choice, *args, **kwargs):
        super(FileSearchForm, self).__init__(*args, **kwargs)

        self.fields['field_list'].choices = field_list_choice



class FileUserSearchForm(forms.Form):
    search = forms.CharField(max_length=255,label=_('Username or email'), required=False, widget=forms.TextInput(
        attrs={'placeholder': _('Username or email...'), 'autocomplete': 'off',
               'class': 'form-control', }))
    permission_type = forms.ChoiceField(choices=FILETYPES_CHOICES,label=_('Permission type'),  required=False, widget=forms.Select(attrs={'placeholder': _('Permission type'), 'autocomplete': 'off','class': 'form-control', }))
    def __init__(self, *args, **kwargs):
        super(FileUserSearchForm, self).__init__(*args, **kwargs)




class AddNewUserPermissionForm(forms.Form):
    user_username_email = forms.CharField(label=_('Username or email'), required=True, widget=forms.TextInput(attrs={'placeholder': _('Username or email'), 'autocomplete': 'off','class': 'form-control border-input', }))

    user_id = forms.IntegerField(required=True, widget=forms.HiddenInput(attrs={'readonly': True, }))
    permission_type = forms.ChoiceField(choices=FILETYPES_CHOICES,label=_('Permission type'),  required=True, widget=forms.Select(attrs={'placeholder': _('Permission type'), 'autocomplete': 'off','required': False,'class': 'form-control', }))
    def __init__(self, *args, **kwargs):
        super(AddNewUserPermissionForm, self).__init__(*args, **kwargs)
