from django.urls import path
from . import views

urlpatterns = [
    path('', views.call_functions, name='calories'),
]