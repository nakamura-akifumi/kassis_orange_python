from django.shortcuts import render_to_response, redirect
from app_search.helpers.message_helper import message
from django.core.context_processors import csrf
from app_search.helpers.paginate_helper import Paginate
from django.http import HttpResponseNotFound
from django.http import HttpResponse
import json
from app_admin.models.location import Location
from app_admin.models.location_form import LocationForm
from django.contrib.auth.models import User
from app_accounts.forms import UserForm
from app_accounts.forms import UserProfileForm
import datetime

# Create your views here.
def location(request, pk):

    print("pk={}".format(pk))
    l = Location.find(pk)
    if l == None or l.exists == False:
        return HttpResponseNotFound(render_to_response('404.html'))

    if request.method == 'POST' and request.POST["_method"] == "DELETE":
        print("delete object id={0}".format(pk))
        l.delete()
        message.flash(request, "削除に成功しました", "success")
        return redirect('locations')

    #
    page = {}
    page.update(message.get_flash_message(request))

    c = {}
    c.update(csrf(request))
    c.update({"l": l.data})
    c.update({"page": page})

    if format == "json":
        return HttpResponse(json.dumps(l.data, ensure_ascii=False, indent=2), content_type='application/json; encoding=utf-8')
    else:
        return render_to_response('locations/show.jinja', c)

def locations(request):

    paginate = Paginate()
    users = User.all()

    c = {}
    c.update(csrf(request))
    page = {}
    page.update(message.get_flash_message(request))
    page.update(paginate.paginate(0, 1))
    c["page"] = page
    c["users"] = users
    return render_to_response('locations/index.jinja', c)

def new_location(request):
    c = {}
    c.update(csrf(request))
    page = {}
    page.update(message.get_flash_message(request))
    page.update({'form': LocationForm()})
    c["page"] = page
    return render_to_response('locations/new.jinja', c)

def user(request, pk):

    u = User.objects.get(id=pk)
    if u == None:
        return HttpResponseNotFound(render_to_response('404.html'))

    p = u.userprofile
    print(">>> start update")
    print(p.id)

    if request.method == 'POST' and request.POST["_method"] == "EDIT":
        print(">>> edit object id={0}".format(pk))
        from app_search.helpers.app_helper import AppHelper
        data = request.POST.copy()
        uform = UserForm(data, instance=u)
        pform = UserProfileForm(data, instance=p)
        if uform.is_valid() and pform.is_valid():
            u = uform.save()
            p = pform.save(commit = False)
            p.user = u
            p.save()
            if user and p:
                message.flash(request, "更新に成功しました", "success")
                # TODO: passwordの通知方法
                return redirect('user', pk = u.id)
            else:
                message.flash(request, "更新に失敗しました", "danger")

        else:
            print(">>> invalid")
            print(uform.errors)
            print(pform.errors)
            message.flash_with_errors(request, "入力エラーです。", uform.errors, pform.errors)


            c = {}
            c.update(csrf(request))
            page = {}
            page.update(message.get_flash_message(request))
            page.update({'id': u.id})
            page.update({'form': UserForm(instance=u)})
            page.update({'profile_form': UserProfileForm(instance=p)})
            c["page"] = page
            return render_to_response('users/edit.jinja', c)

    if request.method == 'POST' and request.POST["_method"] == "DELETE":
        print("delete object id={0}".format(pk))
        u.delete()
        message.flash(request, "削除に成功しました", "success")
        return redirect('users')

    #
    page = {}
    page.update(message.get_flash_message(request))

    c = {}
    c.update(csrf(request))
    c.update({"u": u})
    c.update({"p": p})
    c.update({"page": page})

    if format == "json":
        return HttpResponse(json.dumps(u.data, ensure_ascii=False, indent=2), content_type='application/json; encoding=utf-8')
    else:
        return render_to_response('users/show.jinja', c)


def users(request):
    if request.method == 'POST' and request.POST["_method"] == "NEW":
        from app_search.helpers.app_helper import AppHelper
        data = request.POST.copy()
        data['date_joined'] = datetime.date.today()
        data['is_active'] = True
        print("before")
        print(data)
        if 'password' not in data or 'password' in data and data['password'] == '':
            print("generate password")
            data['password'] = AppHelper.generate_password()

        print("@@@ password={0}".format(data['password']))
        uform = UserForm(data)
        pform = UserProfileForm(data)
        if uform.is_valid() and pform.is_valid():
            u = uform.save()
            p = pform.save(commit = False)
            p.user = u
            p.save()
            if user and p:
                message.flash(request, "登録に成功しました", "success")
                # TODO: passwordの通知方法
                return redirect('user', pk = user.id)
            else:
                message.flash(request, "登録に失敗しました", "danger")

        else:
            message.flash_with_errors(request, "入力エラーです。", uform.errors, pform.errors)

        # end of POST
        c = {}
        c.update(csrf(request))
        page = {}
        page.update(message.get_flash_message(request))
        page.update({'form': uform})
        c["page"] = page
        return render_to_response('users/new.jinja', c)

    paginate = Paginate()
    users = User.objects.all()

    c = {}
    c.update(csrf(request))
    page = {}
    page.update(message.get_flash_message(request))
    page.update(paginate.paginate(0, 1))
    c["page"] = page
    c["users"] = users
    return render_to_response('users/index.jinja', c)

def new_user(request):
    c = {}
    c.update(csrf(request))
    page = {}
    page.update(message.get_flash_message(request))
    page.update({'form': UserForm()})
    page.update({'profile_form': UserProfileForm()})
    c["page"] = page
    return render_to_response('users/new.jinja', c)

def edit_user(request, pk):
    u = User.objects.get(id=pk)
    if u == None:
        return HttpResponseNotFound(render_to_response('404.html'))

    p = u.userprofile

    c = {}
    c.update(csrf(request))
    page = {}
    page.update(message.get_flash_message(request))
    page.update({'id': u.id})
    page.update({'form': UserForm(instance=u)})
    page.update({'profile_form': UserProfileForm(instance=p)})
    c["page"] = page
    return render_to_response('users/edit.jinja', c)
