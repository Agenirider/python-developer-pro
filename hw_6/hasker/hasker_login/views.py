from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout

# Create your views here.


def login(request):
    # username = request.POST['username']
    # password = request.POST['password']
    # user = authenticate(request, username=username, password=password)

    return render(request, 'login.html')


def logout(request):
    logout(request)
    return HttpResponseRedirect('/login')


