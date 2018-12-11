from django.contrib import admin
from .models import Recipe
from .models import Ingredient
from .models import Food
from .models import VegetarianFood, MeasureTable

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Food)
admin.site.register(VegetarianFood)
admin.site.register(MeasureTable)