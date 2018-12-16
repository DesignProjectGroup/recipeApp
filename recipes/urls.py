from django.urls import path
from . import views
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.select_ingredients, name='home'),
    path('suggested_recipes', views.list_recipes, name='suggested_recipes'),
    path('manager_page', views.create_recipes_db, name='manager_page'),
    url(r'recipe/(?P<pk>\d+)/$', views.get_recipe_page, name='get_recipe_page')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
