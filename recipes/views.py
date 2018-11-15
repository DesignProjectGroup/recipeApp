# from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from recipes.models import Recipe
from recipes.models import Food, Recipe, Ingredient
from django.shortcuts import render


def call_functions(request):
    #get_all_recipes()
    #calculate_calories()
    return render(request, 'recipes/home_page.html', {})


def calculate_calories():
    ingredients = Ingredient.objects.order_by('count')
    foods = Food.objects.order_by('name')
    for ingredient in ingredients:
        recipe = Recipe.objects.get(id=ingredient.recipe.id)
        for food in foods:
            if ingredient.id == food.ingredient.id:
                recipe.calorie += (food.calorie/food.unit_amount)*food.ingredient.count
                recipe.save()
    #rec = Recipe.objects.order_by('title')
    #for r in rec:
        #print(r.title, r.calorie)


def get_all_recipes():
    r = requests.get('http://www.ardaninmutfagi.com/')
    soup = BeautifulSoup(r.content, "html.parser")
    all_categories = soup.find_all("div", attrs={"class": "arda-menu-ck-liste"})
    for categories in all_categories:
        for category in categories.find_all("li"):
            category_link = category.a.get("href")
            get_recipe_link(category_link)


def get_recipe_link(parent_category_link):
    r = requests.get(parent_category_link)
    soup = BeautifulSoup(r.content, "html.parser")
    for i in soup.find_all("div", attrs={"class": "icerik-card-box"}):
        recipe_link = i.find("article").a.get("href")
        get_recipe(recipe_link)


# recipe_title
# recipe_ingredient_title
# recipe_ingredients_list
# recipe_preparation_steps_list
def get_recipe(recipe_link):
    recipe_ingredients_list = []
    recipe_preparation_steps_list = ""
    r = requests.get(recipe_link)
    soup = BeautifulSoup(r.content, "html.parser")
    # recipe_title
    recipe_title = soup.find("h1", attrs={"class": "entry-title"}).text

    # recipe_ingredient_title
    if soup.find("strong"):
        recipe_ingredient_title = soup.find("strong").text

    # recipe_ingredients_list
    if soup.find("div", attrs={"class": "mlz"}):
        ingredients = soup.find("div", attrs={"class": "mlz"}).find_all("br")
        for i in ingredients:
            recipe_ingredients_list.append(i.next_sibling.replace("\n", ""))

    # recipe_preparation_steps_list
    recipe_preparation_steps = soup.find("div", attrs={"class": "entry-content"}).find_all("p")
    for p in recipe_preparation_steps:
        if not p.text == "":
            recipe_preparation_steps_list = recipe_preparation_steps_list + p.text + "\n"

    if soup.find("strong") and soup.find("div", attrs={"class": "mlz"}):
        Recipe.objects.update_or_create(title=recipe_title, text=recipe_preparation_steps_list,
                                        ingredient_title=recipe_ingredient_title)



