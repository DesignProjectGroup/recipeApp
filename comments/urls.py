from django.urls import path
from . import views

urlpatterns = [
    path('', views.deneme, name='comment_template'),

]