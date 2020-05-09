import datetime

from django.shortcuts import render

# Create your views here.
from app.settings import MAX_FILE_UPLOAD_LIMIT


def base(req=None):

    data = {
        'now':datetime.datetime.now(),
    }
    return data


def base_auth(req=None):

    data = {
        'now':datetime.datetime.now(),
        'MAX_FILE_UPLOAD_LIMIT':MAX_FILE_UPLOAD_LIMIT,
    }
    return data
