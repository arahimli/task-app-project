import datetime

from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from core.models import UserLoginLog
from core.views import base
# Function based views to Class Based Views
from user_app.forms import CustomUserCreationForm
from user_app.models import UserConfrimationKeys


def login_view(request, *args, **kwargs):
    form = AuthenticationForm(request, data=request.POST or None)

    context = base(req=request)
    if request.method == 'POST':
        if  form.is_valid():
            user_ = form.get_user()
            user = login(request, user_)
            print(user_)
            next = request.GET.get('next',None)
            if next is None:
                next = reverse('content-app:dashboard')
            return redirect(next)
        else:
            messages.error(request, 'Your username or password is incorrect')

    context.update({
        "form": form,
        "btn_label": _("Login"),
        "page_title": _("Log-in to your account")
    })
    return render(request, "login.html", context)



def logout_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        logout(request)

    next_url = reverse('user-app:login')
    return HttpResponseRedirect(next_url)


def register_view(request, *args, **kwargs):
    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=True)
            user.set_password(form.cleaned_data.get("password1"))
            login(request, user)
            messages.info(request, 'You have registered successfully. Please confirm your account')
            return redirect(reverse("user-app:login"))
        else:
            print(form.errors)
    context = {
        "form": form,
        "btn_label": "Register",
        "page_title": "Register"
    }
    return render(request, "register.html", context)


def verify_view(request, uuid):
    try:
        user = UserConfrimationKeys.objects.get(key=uuid, expired=False,expired_date__gte=datetime.datetime.now())
        user.expired = True
        user.user.is_active = True
        user.save()
        user.user.save()
        return HttpResponseRedirect(reverse('content-app:dashboard'))
    except UserConfrimationKeys.DoesNotExist:
        raise Http404("User does not exist or is already verified")
