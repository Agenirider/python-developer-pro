from django.urls import path
from . import views


urlpatterns = [
    path('', views.get_start_page, name='get start page'),
]
