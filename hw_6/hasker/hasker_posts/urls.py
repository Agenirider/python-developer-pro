from django.urls import path
from . import views


urlpatterns = [
    path('get_posts', views.get_posts, name='get all posts'),
    path('search', views.get_posts, name='get all posts'),
]
