import datetime
import os
import uuid

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


# Create your models here.
from content.managers.shared_file_manager import SharedFileModelManager
from core._tools.choices import FILETYPES_CHOICES
from core.functions import file_path_and_rename


class SharedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="+",on_delete=models.CASCADE)
    title = models.CharField(_('Title'),max_length=255,default=_('Untitled'))
    file = models.FileField(upload_to=file_path_and_rename)
    description = models.TextField(_('Description'),null=True)
    active = models.BooleanField(default=False)
    expiration_date = models.DateTimeField(_('Expiration date'),default=datetime.datetime.now() + datetime.timedelta(hours=5))
    updated_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    objects = SharedFileModelManager()
    def __str__(self):
        return self.title
    def get_user_permission(self,user):
        return SharedFileUser.objects.filter(shared_file=self,user=user)

@receiver(models.signals.post_delete, sender=SharedFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

@receiver(models.signals.pre_save, sender=SharedFile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = SharedFile.objects.get(pk=instance.pk).file
    except SharedFile.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class SharedFileUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="+",on_delete=models.CASCADE)
    shared_file = models.ForeignKey('SharedFile',on_delete=models.CASCADE,related_query_name='user_shared_file',related_name='user_shared_file_name')
    permission_type = models.CharField(_('Permission type'),max_length=255,choices=FILETYPES_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "{} - {}".format(self.user.get_full_name(), self.shared_file.title)

    def get_permission_type(self):
        return_val = self.permission_type
        for item in FILETYPES_CHOICES:
            if item[0] == self.permission_type:
                return_val = item[1]
                break
        return return_val

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="+",on_delete=models.CASCADE)
    shared_file = models.ForeignKey('SharedFile',related_name="+",on_delete=models.CASCADE,related_query_name='comment_shared_file')
    text = models.TextField( _('Text') )
    updated_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "{} - {}".format(self.user.get_full_name(), self.shared_file.title)

