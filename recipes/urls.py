from . import views
from django.conf.urls import url
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.select_ingredients, name='home'),
    path('suggested_recipes', views.list_recipes, name='suggested_recipes'),
    path('manager_page', views.create_recipes_db, name='manager_page'),
    url(r'recipe/(?P<pk>\d+)/$', views.get_recipe_page, name='get_recipe_page'),
    path('suggested_recipes/alphabetic_sort', views.list_recipes, name='alphabetic_sort'),
    path('suggested_recipes/calorie_sort', views.list_recipes, name='calorie_sort'),
    path('suggested_recipes/easy_hard_sort', views.list_recipes, name='easy_hard_sort'),
    path('suggested_recipes/by_comment_sort', views.list_recipes, name='by_comment_sort')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
