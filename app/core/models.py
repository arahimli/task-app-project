from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.



class UserLoginLog(models.Model):
    user = models.IntegerField('User id', null=True,blank=True)
    ip = models.CharField(max_length=15,null=True, blank=True)
    browser = models.CharField(max_length=100,null=True, blank=True)
    os = models.CharField(max_length=100,null=True, blank=True)
    device = models.CharField(max_length=100,null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ('-date',)
        verbose_name = _("User login log")
        verbose_name_plural = _("User login log")
    #
    # def __str__(self):
    #     return "{} - {}".format(self.user.get_full_name(),self.ip)
