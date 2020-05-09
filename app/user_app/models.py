from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core import validators
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
import uuid
from django.db.models import signals
# from work.common import *
# My custom tools import
from datetime import datetime, timedelta
# Create your models here.
from core._tools.choices import USERTYPES_CHOICES

from core.functions import file_path_and_rename
from user_app.tasks import send_html_mail
from core.models import UserLoginLog



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """ Create ans ave new user """
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """ Create ans ave new user """
        user = self.create_user(email,password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


# Customize User model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username, password and email are required. Other fields are optional.
    """

    username = models.CharField(_('username'), max_length=100, unique=True,
                                help_text=_('Character length may be maxiumum 100'),
                                validators=[
                                    validators.RegexValidator(r'^[\w.@+-]+$', _('Type correct username'),
                                                              'wrong')
                                ]
                                )
    first_name = models.CharField(_('First name'), max_length=255, blank=True)
    last_name = models.CharField(_('Last name'), max_length=255, blank=True)
    email = models.EmailField(_('Email address'), max_length=255,unique=True)
    # birthdate = models.DateField(verbose_name="Birth day",blank=True,null=True)
    profile_picture = models.ImageField(upload_to=file_path_and_rename, null=True, blank=True)
    verified = models.BooleanField(default=False, verbose_name="Verified")
    phone = models.CharField(max_length=100, verbose_name="Phone", null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)

    usertype = models.IntegerField(choices=USERTYPES_CHOICES, verbose_name="User Type", null=True, blank=True)
    is_staff = models.BooleanField(_('Staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('Active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)


    # objects = CustomUserManager()
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name
    def __str__(self):
        return "{} {}".format(self.first_name,self.last_name)

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        self.slug = slugify("{}{}".format(self.first_name,str(timezone.now().timestamp()).replace('.','-')))
        super(CustomUser, self).save(*args, **kwargs)

def user_save(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        # print(signal)
        # Send verification email
        confirm_obj = UserConfrimationKeys(key=uuid.uuid4(),user=instance,expired_date=datetime.now()+timedelta(days=7),expired=False)
        confirm_obj.save()
        # try:
        # send_html_mail.delay(instance.email,
        #                      _("Confirm your email"),
        #                      '<a href="{}">{}</a>'.format(reverse('user-app:verify',kwargs={'uuid':confirm_obj.key}),_('Click here to confirm your account'))
        #                      )
        # except:
        #     pass

signals.post_save.connect(user_save, sender=CustomUser)

from django.contrib.auth.signals import user_logged_in


def do_stuff(sender, user, request, **kwargs):
    from user_agents import parse

    # iPhone's user agent string
    ua_string = request.META['HTTP_USER_AGENT']
    user_agent = parse(ua_string)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    UserLoginLog.objects.using('core_db').create(user=user.id,
                                                 ip=ip,
                                                 browser="{} {}".format(user_agent.browser.family,user_agent.browser.version_string),
                                                 os="{} {}".format(user_agent.os.family,user_agent.os.version_string),
                                                 device="{} {} {}".format(user_agent.device.family, user_agent.device.brand, user_agent.device.model),
                                                 )
    print("--------------------------------------------------------------------------------")

user_logged_in.connect(do_stuff)

class UserConfrimationKeys(models.Model):
    key = models.CharField(max_length=255,null=True, blank=True)
    user = models.ForeignKey('CustomUser', null=True,blank=True,on_delete=models.CASCADE)
    expired_date = models.DateTimeField()
    expired = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date',)
        verbose_name = _("Confirmed user")
        verbose_name_plural = _("Confirmed users")

    def __str__(self):
        return "{}".format(self.key)
