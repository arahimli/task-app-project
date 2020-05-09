from django.urls import path

from content.views import dashboard_view, settings_view, add_file_view, file_list_view, edit_file_view, \
    details_file_view, remove_file_view, remove_comment_view, details_file_get_comments_view, file_permission_list_view, \
    remove_permission_file_view, user_list_ajax, add_permission_file_view
from user_app.views import login_view, logout_view, register_view

app_name = 'content-app'
urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('settings/<slug:slug>/', settings_view, name='settings'),
    path('files/list/', file_list_view, name='file-list'),
    path('files/add/', add_file_view, name='add-file'),
    path('files/edit/<slug:id>/', edit_file_view, name='file-edit'),
    path('files/permission-list/<slug:id>/', file_permission_list_view, name='file-permission-list'),
    path('files/permission-remove/<slug:id>/', remove_permission_file_view, name='file-permission-remove'),
    path('files/permission-add/<slug:id>/', add_permission_file_view, name='file-permission-add'),
    path('files/user-list/', user_list_ajax, name='user-list'),
    path('files/details/<slug:id>/', details_file_view, name='file-details'),
    path('files/details/<slug:id>/get-comments/', details_file_get_comments_view, name='file-details-get-comments'),
    path('files/remove/<slug:id>/', remove_file_view, name='file-remove'),
    path('comments/remove/<slug:id>/', remove_comment_view, name='comments-remove'),
]