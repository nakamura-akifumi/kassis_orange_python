from django.shortcuts import render
from django.shortcuts import render_to_response, redirect
from app_search.helpers.message_helper import message
from django.core.context_processors import csrf
from django.http import HttpResponseNotFound
from django.http import HttpResponse
import json

# Create your views here.
def profile(request):
    print(request.user)
    u = request.user
    if u == None:
        return HttpResponseNotFound(render_to_response('404.html'))

    page = {}
    page.update(message.get_flash_message(request))

    c = {}
    c.update(csrf(request))
    c.update({"u": u})
    c.update({"page": page})

    return render_to_response('accounts/profile.jinja', c)


