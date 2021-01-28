from django.urls import path
from . import views


urlpatterns = [
    path('login', views.login, name='authenticate user'),
    path('logout', views.logout, name='user logout'),
]
