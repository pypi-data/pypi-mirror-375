# src/cs_robots/urls.py
from django.urls import path
from .views import edit_robots_txt

app_name = 'cs_robots' 

urlpatterns = [
    path('edit-robots-txt/', edit_robots_txt, name='edit_robots_txt'),
]