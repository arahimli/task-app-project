import copy
import datetime
import time

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.forms import inlineformset_factory
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from django.urls import reverse

from content.forms import SharedFileUserForm, SharedFileForm, FileSearchForm, CommentForm, SharedFileOnlyFileForm, \
    FileUserSearchForm, AddNewUserPermissionForm
from content.models import SharedFile, SharedFileUser, Comment
from core._tools.choices import SHAREDFILEMODEL_CHOICES, FILETYPES_CHOICES
from core.views import base_auth
from user_app.forms import CustomUserChangeResForm
User = get_user_model()
# Create your views here.


@login_required(login_url='user-app:login')
def dashboard_view(request, *args, **kwargs):
    if request.method=='GET':
        context = base_auth(req=request)
        context.update({
            "form": None,
            "description": "Are you sure you want to logout?",
            "btn_label": "Click to Confirm",
            "title": "Logout"
        })
        return render(request, "pages/dashboard.html", context)
    else:
        user = request.user
        if request.is_ajax():
            data_list = SharedFile.objects.filter(Q(author=user) | Q(user_shared_file__user=user)).distinct()
            data = {
                'all_data_count':data_list.count(),
            }
            data['private_data_count'] = data_list.filter(author=user).count()
            data['shared_data_count'] = data['all_data_count'] -  data['private_data_count']
            return JsonResponse(data=data)
        else:
            raise Http404

@login_required(login_url='user-app:login')
def settings_view(request, slug, *args, **kwargs):
    context = base_auth(req=request)
    context['slug'] = slug
    if slug == 'change-password':
        context['page_title'] = _("Password change")
        context['page_description'] = _("Password change form")
        context['page_icon'] = "key"

        context['next_page_title'] = _("Profile change")
        context['next_page_description'] = _("Profile change form")
        context['next_page_url'] = reverse('content-app:settings' ,kwargs={'slug':'change-profile'})
        context['next_page_icon'] = "user"
        context['btn_label'] = _("Change")
        form = PasswordChangeForm(data=request.POST or None, user=request.user)
        if request.method == "POST" and form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            next_url = reverse('content-app:settings',kwargs={'slug':slug})
            messages.success(request, 'You have changed your password successfully')
            return HttpResponseRedirect(next_url)
        else:
            context['form'] = form
            return render(request, "pages/settings/change-password.html", context)
    elif slug == 'change-profile':
        context['page_title'] = _("Profile change")
        context['btn_label'] = _("Change")
        context['page_description'] = _("Profile change form")
        context['page_icon'] = "user"
        context['next_page_title'] = _("Password change")
        context['next_page_description'] = _("Password change form")
        context['next_page_url'] = reverse('content-app:settings' ,kwargs={'slug':'change-password'})
        context['next_page_icon'] = "key"
        form = CustomUserChangeResForm(data=request.POST or None, instance=request.user)
        if request.method == "POST" and form.is_valid():

            form.save()
            # update_session_auth_hash(request, form.user)
            next_url = reverse('content-app:settings',kwargs={'slug':slug})
            messages.success(request, 'You have changed your profile infomation successfully')
            return HttpResponseRedirect(next_url)
        else:
            context['form'] = form
            return render(request, "pages/settings/change-password.html", context)
    else:
        raise Http404





@login_required(login_url='user-app:login')
def file_list_view(request, *args, **kwargs):
    context = base_auth(req=request)
    context['page_title'] = _("Your shared file list")
    context['page_description'] = _("Your shared file list")
    context['page_icon'] = "download"
    context['btn_label'] = _("Share new file")
    inital_data = {
        'order_type':'-',
        'field_list':'created_date',
    }
    PAGE_DATA_COUNT = 5
    user = request.user
    search_form = FileSearchForm(SHAREDFILEMODEL_CHOICES, request.POST or None, initial=inital_data)
    if request.method=='POST' and request.is_ajax():
        if search_form.is_valid():
            cleaned_data = search_form.cleaned_data
            search_text = cleaned_data.get('search',None)
            field_list = cleaned_data.get('field_list',None)
            start_date = cleaned_data.get('start_date',None)
            end_date = cleaned_data.get('end_date',None)
            order_type = cleaned_data.get('order_type',None)
            data_list = SharedFile.objects.filter(Q(author=user) | Q(user_shared_file__user=user)).order_by('{}{}'.format(order_type,field_list)).distinct()
            if search_text:
                data_list = data_list.filter(Q(title__icontains=search_text) | Q(description__icontains=search_text))
            if start_date:
                start_date_min = datetime.datetime.combine(start_date, datetime.time.min)
                data_list = data_list.filter(created_date__gte=start_date_min)
            if end_date:
                end_date_max = datetime.datetime.combine(end_date, datetime.time.max)
                data_list = data_list.filter(created_date__lte=end_date_max)
            try:
                page_num = int(request.POST.get('page-num', 2))
            except:
                page_num = 0
            _list_item_html = ''
            _paginated_html = ''
            paginator = Paginator(data_list, PAGE_DATA_COUNT)
            try:
                data_list_obj = paginator.page(page_num)
            except PageNotAnInteger:
                data_list_obj = paginator.page(PAGE_DATA_COUNT)
            except EmptyPage:
                data_list_obj = paginator.page(paginator.num_pages)
            if data_list_obj:
                for data_item in data_list_obj:
                    _list_item_html = "{}{}".format(_list_item_html,render_to_string(
                        "pages/files/_include/list-item.html",
                    {
                        "data_item":data_item,
                        "user":user,
                        'base_profile': request.user,
                    }))
            if data_list_obj.has_other_pages:
                    # for_i+=1
                _paginated_html = "{}{}".format(_paginated_html,render_to_string(
                    "pages/files/_include/pagination.html",
                {
                    "data_list_obj":data_list_obj,
                }))


            main_html = _list_item_html
            data = {
                'main_result':"{}".format(main_html),
                'paginated_html':"{}".format(_paginated_html),
                # 'data_count':data_count,
            }
        else:
            data = {
                'main_result':"{}".format(str(search_form.errors)),
                'paginated_html':'',
            }
        return JsonResponse(data=data)
    # else:
    #     log_generation.delay(title=title, user_id=request.user.id, object_data='Customer',
    #                          operation='show', content='',
    #                          url=request.build_absolute_uri())
    context['search_form'] = search_form
    return render(request, "pages/files/list.html", context)


@login_required(login_url='user-app:login')
def add_file_view(request, *args, **kwargs):
    context = base_auth(req=request)


    context['page_title'] = _("Upload and share new file")
    context['page_description'] = _("Upload and share new file form")
    context['page_icon'] = "download"
    context['btn_label'] = _("Upload and pass to edit page")

    shared_file = SharedFile()

    if request.method == 'GET':
        form = SharedFileOnlyFileForm(instance=shared_file)
    else:
        form = SharedFileOnlyFileForm(request.POST, request.FILES, instance=shared_file)

        if form.is_valid():
            form_val = form.save(commit=False)
            form_val.author = request.user
            form_val.save()
            messages.info(request=request, message=_("The file uploaded successfully. You have to type the form"))
            data = {'code':1,'url': reverse('content-app:file-edit', kwargs={'id': form_val.id})}
        else:
            data = {'code':0,'message':form.errors,}
        return JsonResponse(data=data)

    context.update({
        'user': request.user,
        'request': request
    })
    context.update(csrf(request))
    context['form'] = form
    return render(request, "pages/files/file-upload-form.html", context)




@login_required(login_url='user-app:login')
def edit_file_view(request, id, *args, **kwargs):
    context = base_auth(req=request)


    context['page_title'] = _("Share edit file")
    context['page_description'] = _("Share edit file form")
    context['page_icon'] = "download"
    context['btn_label'] = _("Share edit file")


    shared_file_obj = get_object_or_404(SharedFile,id=id,author=request.user,expiration_date__gte=datetime.datetime.now())

    context['file_user_search_form'] = FileUserSearchForm()
    context['add_new_user_permission_form'] = AddNewUserPermissionForm()
    if request.method == 'GET':
        form = SharedFileForm(instance=shared_file_obj)
    else:
        form = SharedFileForm(request.POST, request.FILES, instance=shared_file_obj)

        if form.is_valid():
            form_val = form.save(commit=False)
            form_val.active = True
            form_val.save()

            messages.success(request=request, message=_("File have changed successfully"))
            return HttpResponseRedirect(reverse('content-app:file-list'))

    context.update({
        'user': request.user,
        'form': form,
        'request': request,
        'shared_file_obj': shared_file_obj,
    })
    context.update(csrf(request))
    context['form'] = form
    return render(request, "pages/files/form.html", context)


@login_required(login_url='user-app:login')
def file_permission_list_view(request, id, *args, **kwargs):
    context = base_auth(req=request)
    context['page_title'] = _("Your shared file list")
    context['page_description'] = _("Your shared file list")
    context['page_icon'] = "download"
    context['btn_label'] = _("Share new file")
    inital_data = {
    }
    PAGE_DATA_COUNT = 2
    user = request.user
    search_form = FileUserSearchForm(request.POST or None, initial=inital_data)
    if request.method=='POST' and request.is_ajax():
        if search_form.is_valid():
            cleaned_data = search_form.cleaned_data
            search_text = cleaned_data.get('search',None)
            permission_type = cleaned_data.get('permission_type',None)

            data_list = SharedFileUser.objects.filter(shared_file_id=id, shared_file__author=request.user)
            if search_text:
                data_list = data_list.filter(Q(user__email__icontains=search_text) | Q(user__username__icontains=search_text))
            if permission_type:
                data_list = data_list.filter(permission_type=permission_type)
            try:
                page_num = int(request.POST.get('page-num', 1))
            except:
                page_num = 0
            _list_item_html = ''
            _paginated_html = ''
            paginator = Paginator(data_list, PAGE_DATA_COUNT)
            try:
                data_list_obj = paginator.page(page_num)
            except PageNotAnInteger:
                data_list_obj = paginator.page(PAGE_DATA_COUNT)
            except EmptyPage:
                data_list_obj = paginator.page(paginator.num_pages)
            # data_list = data_list[50 * (page_num - 1):50 * page_num]
            if data_list_obj:
                for data_item in data_list_obj:
                    _list_item_html = "{}{}".format(_list_item_html,render_to_string(
                        "pages/files/_include/permission/permission-user-item.html",
                    {
                        "data_item":data_item,
                        "user":user,
                        'base_profile': request.user,
                    }))
            if data_list_obj.has_other_pages:
                _paginated_html = "{}{}".format(_paginated_html,render_to_string(
                    "pages/files/_include/permission/pagination.html",
                {
                    "data_list_obj":data_list_obj,
                }))


            main_html = _list_item_html
            data = {
                'main_result':"{}".format(main_html),
                'paginated_html':"{}".format(_paginated_html),
                # 'data_count':data_count,
            }
        else:
            data = {
                'main_result':"{}".format(str(search_form.errors)),
                'paginated_html':'',
            }
        return JsonResponse(data=data)
    # else:
    #     log_generation.delay(title=title, user_id=request.user.id, object_data='Customer',
    #                          operation='show', content='',
    #                          url=request.build_absolute_uri())
    context['search_form'] = search_form
    return render(request, "pages/files/list.html", context)



@login_required(login_url='user-app:login')
def details_file_view(request, id, *args, **kwargs):
    context = base_auth(req=request)
    try:
        shared_file_obj = SharedFile.objects.filter(id=id,expiration_date__gte=datetime.datetime.now()).filter(Q(author=request.user) | Q(user_shared_file__user=request.user)).distinct().get()
    except:
        raise Http404
    comment_form = CommentForm()
    if shared_file_obj.author == request.user or shared_file_obj.user_shared_file_name.filter(user=request.user,permission_type=FILETYPES_CHOICES[2][0]):
        context['comment_form'] = comment_form
    context['page_title'] = shared_file_obj.title
    context['page_icon'] = "download"
    context['shared_file_obj'] = shared_file_obj



    return render(request, "pages/files/details.html", context)


@login_required(login_url='user-app:login')
def remove_file_view(request, id, *args, **kwargs):
    if request.method == 'POST' and request.is_ajax():
        code = 0
        try:
            shared_file_obj = get_object_or_404(SharedFile,id=id,author=request.user,expiration_date__gte=datetime.datetime.now())
            shared_file_obj.delete()
            code = 1
        except:
            pass
        return JsonResponse(data={'code':code})
    else:
        raise Http404

@login_required(login_url='user-app:login')
def details_file_get_comments_view(request, id, *args, **kwargs):
    context = base_auth(req=request)

    PAGE_DATA_COUNT = 7
    shared_file_obj = get_object_or_404(SharedFile,id=id,expiration_date__gte=datetime.datetime.now())

    if request.method=='POST' and request.is_ajax():
        # time.sleep(0.1)
        next_page = False
        page_num = 1
        try:
            # page_num = int(request.POST.get('page-num', 1))
            last_cid = int(request.POST.get('last-cid', 0))
        except:
            last_cid = 0
        comment_list = Comment.objects.filter(shared_file=shared_file_obj)
        if last_cid:
            comment_list = comment_list.filter(shared_file=shared_file_obj).filter(id__lt=last_cid)
        comment_count = copy.deepcopy(comment_list.count())
        if comment_count > PAGE_DATA_COUNT:
            next_page = True
        comment_list = comment_list.order_by('-created_date')[PAGE_DATA_COUNT * (page_num - 1):PAGE_DATA_COUNT * page_num]
        _comment_html = ''
        if comment_list:

            page_num += 1
            for comment_item in comment_list:
                _comment_html = "{}{}".format(render_to_string(
                    "pages/files/_include/comment-item.html",
                {
                    "comment_item": comment_item,
                    "user": request.user,
                }),_comment_html)
                last_cid = comment_item.id
        return JsonResponse(data={'last_cid':last_cid, 'page_num':page_num, 'next_page':next_page, 'comment_html':_comment_html})
    else:
        raise Http404




@login_required(login_url='user-app:login')
def remove_comment_view(request, id, *args, **kwargs):
    if request.method == 'POST' and request.is_ajax():
        code = 0
        try:
            data_item_obj = get_object_or_404(Comment,id=id,user=request.user)
            data_item_obj.delete()
            code = 1
        except:
            pass
        return JsonResponse(data={'code':code})
    else:
        raise Http404

@login_required(login_url='user-app:login')
def remove_permission_file_view(request, id, *args, **kwargs):
    if request.method == 'POST' and request.is_ajax():
        code = 0
        try:
            data_obj = get_object_or_404(SharedFileUser,id=id,shared_file__author=request.user)
            data_obj.delete()
            code = 1
        except:
            pass
        return JsonResponse(data={'code':code})
    else:
        raise Http404


@login_required(login_url='user-app:login')
def add_permission_file_view(request,id, *args, **kwargs):

    add_new_user_permission_form = AddNewUserPermissionForm(request.POST)
    if request.method == 'POST' and request.is_ajax():
        code = 0
        if add_new_user_permission_form.is_valid():
            cleaned_data = add_new_user_permission_form.cleaned_data
            user_id = cleaned_data.get('user_id',None)
            permission_type = cleaned_data.get('permission_type',None)
            try:
                data_obj = SharedFile.objects.filter(id=id,author=request.user).get()
                obj, created = SharedFileUser.objects.get_or_create(user_id=user_id,shared_file=data_obj,permission_type=permission_type)
                if created:
                    result_message = _('Permission added successfully')
                    code = 1
                else:
                    result_message = _('This permission already added')
            except:
                result_message = _('You can not add this permission to this user')
        else:
            result_message  = _('Please type correct data to the form')
        return JsonResponse(data={'code':code,'result_message':result_message})
    else:
        raise Http404




@login_required(login_url='base-user:login')
def user_list_ajax(request):

    if request.method=='POST' and request.is_ajax():
        search = request.POST.get('user_username_email',None)
        _result_message = ''
        _result_html = ''
        _result_code = 0
        if search and str(search).lstrip() != '':
            search = str(search).lstrip()
            user_list = User.objects.exclude(id=request.user.id).filter(Q(email=search) | Q(username=search))
            if user_list:
                _result_code = 1
                for user_item in user_list.order_by('username'):
                    _result_html = "{}{}".format(_result_html,
                                                 '<tr>'
                                                     '<td >{}</td>'
                                                     '<td>{}</td>'
                                                 '</tr>'.format(
                                                     user_item.get_full_name(),
                                                     '<a id="user-button-item-{}" onclick="selectCustomer({},\'{}\',)" href="javascript:void(0);" class="customer-button-item ui basic primary button">{}</a>'.format(user_item.id,user_item.id,user_item.get_full_name(),_('Select')),
                                                 )
                                                 )
            else:
                _result_message = _('No such user')
        else:
            _result_message = _('You have to type some username or email')
        data = {'main_result':_result_html,'code':_result_code,'result_message':_result_message}
        return JsonResponse(data=data)
    else:
        raise Http404
