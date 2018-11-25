# from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from recipes.models import Recipe
from recipes.models import Food, Recipe, Ingredient
from django.shortcuts import render


selected_food = []
def list_recipes(request):
   return render(request, 'recipes/suggested_recipes.html', {})


def call_functions(request):
    get_all_recipes()
    #calculate_calories()
    foods = Food.objects.all()
    if request.method == 'POST':
        selected_food.append(request.POST.get('selected_food'))
    return render(request, 'recipes/home_page.html', {'foods': foods,'selected_food': selected_food})


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
    ingredients_subtitles_text_list = []
    r = requests.get(recipe_link)
    soup = BeautifulSoup(r.content, "html.parser")

    # recipe_title
    recipe_title = soup.find("h1", attrs={"class": "entry-title"}).text

    # recipe_preparation_steps_list
    recipe_preparation_steps = soup.find("div", attrs={"class": "entry-content"}).find_all("p")
    for p in recipe_preparation_steps:
        if not p.text == "":
            recipe_preparation_steps_list = recipe_preparation_steps_list + p.text + "\n"

    Recipe.objects.update_or_create(title=recipe_title, text=recipe_preparation_steps_list)
    this_recipe = Recipe.objects.get(title=recipe_title, text=recipe_preparation_steps_list)

    # recipe_ingredients_list
    if soup.find("div", attrs={"class": "mlz"}):
        ingredients_subtitles_list = soup.find("div", attrs={"class": "mlz"}).find_all("strong")
        for i in ingredients_subtitles_list:
            ingredients_subtitles_text_list.append(i.text)
        ingredients = soup.find("div", attrs={"class": "mlz"}).find_all("br")

        for i in ingredients:
            recipe_ingredients_list.append(i.next_sibling.replace("\n", ""))

        ingredients_subtitle_number = 0
        for i in recipe_ingredients_list:
            if i == "":
                ingredients_subtitle_number = ingredients_subtitle_number + 1
            else:
                Ingredient.objects.update_or_create(name=i,
                                                    subtitle=ingredients_subtitles_text_list
                                                    [ingredients_subtitle_number],
                                                    recipe=this_recipe)
