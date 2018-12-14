from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.select_ingredients, name='home'),
    path('suggested_recipes', views.list_recipes, name='suggested_recipes'),
    path('manager_page', views.create_recipes_db, name='manager_page'),
    url(r'recipe/(?P<pk>\d+)/$', views.get_recipe_page, name='get_recipe_page')
]
