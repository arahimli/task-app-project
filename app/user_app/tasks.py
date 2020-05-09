# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task


@shared_task
def add(x, y):
    return x + y



@shared_task
def send_html_mail(email,subject,html):
    from django.core.mail import send_mail
    from django.conf import settings
    from django.utils.translation import ugettext_lazy as _
    main_send = send_mail(
        subject=subject,
        html_message=html,
        message='',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False
    )
    return "Mail send result is {}".format(_('yes') if main_send else _('no'))
