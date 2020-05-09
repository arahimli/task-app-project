from django.urls import path

from user_app.views import login_view, logout_view, register_view, verify_view

app_name = 'user-app'
urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('verify-view/<slug:uuid>/', verify_view, name='verify'),
]