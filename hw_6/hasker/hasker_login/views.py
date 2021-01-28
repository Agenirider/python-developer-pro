from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def login(request):
    return HttpResponse('<h1>Login</h1>')


def logout(request):
    return HttpResponse('<h1>Logout</h1>')