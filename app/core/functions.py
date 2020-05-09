import os
from uuid import uuid4
from django.utils.datetime_safe import datetime as datetime_util



def file_path_and_rename(instance, filename):
    now = datetime_util.now()
    upload_to = 'files/{}/{}/{}'.format(now.year,now.month,now.day)
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}-{}.{}'.format(uuid4().hex,instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)

