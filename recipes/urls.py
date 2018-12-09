from django.urls import path
from . import views

urlpatterns = [
    path('', views.select_ingredients, name='calories'),
    path('suggested_recipes', views.list_recipes, name='suggested_recipes'),
    path('manager_page', views.create_recipes_db, name='manager_page'),
]