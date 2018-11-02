from recipes.models import Food, Recipe, Ingredient
from django.shortcuts import render

def calculate_calories(request):
    ingredients = Ingredient.objects.order_by('count')
    foods = Food.objects.order_by('name')
    for ingredient in ingredients:
        recipe = Recipe.objects.get(id=ingredient.recipe.id)
        for food in foods:
            if(ingredient.id == food.ingredient.id):
                recipe.calorie += (food.calorie/food.unit_amount)*food.ingredient.count
                recipe.save()
    rec = Recipe.objects.order_by('title')
    for r in rec:
        print(r.title, r.calorie)
    return render(request, 'recipes/all_cooking_categories.html')
