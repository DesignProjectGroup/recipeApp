from django.contrib import admin
from .models import Recipe
from .models import Ingredient
from .models import Comment
from .models import Food
from .models import VegetarianFood

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Comment)
admin.site.register(Food)
admin.site.register(VegetarianFood)