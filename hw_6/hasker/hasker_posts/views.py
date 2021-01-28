from django.http import HttpResponse
from django.shortcuts import render

def get_posts(request):
    return HttpResponse('<h1>Get Posts</h1>')
