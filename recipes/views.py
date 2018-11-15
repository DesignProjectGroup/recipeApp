# from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from recipes.models import Recipe
from recipes.models import Food, Recipe, Ingredient
from django.shortcuts import render


def call_functions(request):
    #get_all_recipes()
    calculate_calories()
    getLinks_from_trendus()
    return render(request, 'recipes/all_cooking_categories.html', {})


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

def clear_split_string(item):
    if len(item) == 4:
        item[0] = item[0] + " " + item[1]
        del item[1]
    elif len(item) == 5:
        item[0] = item[0] + " " + item[1] + " " + item[2]
        del item[1]
        del item[2]
    return item


def getLinks_from_trendus():
    """ we can using other website like trendus  I was trying to get linke from her"""
    webpage = 'http://www.trendus.com/kalori-cetveli-1933'
    r = requests.get(webpage)
    page_soup = BeautifulSoup(r.content, "html.parser")
    all_items = page_soup.findAll("div", attrs={"class": "News-P"})
    all_items_as_string = str(all_items).rstrip().split('\n')
    by_gram = "gram"
    by_porsiyon = "porsiyon"
    by_adet = "adet"
    by_bardak = "bardak"
    by_Birim = "Birim"
    by_kutu = "kutu"
    by_drim = "dilim"

    print("item      birim     Kalori")
    for item in all_items_as_string:
        if "gram" in item and "bardak" not in item:
            item = item[3:-4].replace('gram', '').split()
            content = clear_split_string(item)
            print(content[0] +"  " +content[1]+" gram    "+content[2])
            Food.objects.update_or_create(name=content[0], calorie=content[2], unit_amount=content[1],
                                          measurement_unit="gram")

        elif "porsiyon" in item:
            item = item[3:-4].replace('porsiyon', '').split()
            content = clear_split_string(item)
            content[1] = "1"
            # print(content[0] + "  " + content[1]+" porsiyon    "+content[2])
            Food.objects.update_or_create(name=content[0], calorie=content[2], unit_amount=content[1],
                                          measurement_unit="porsiyon")

        elif "adet" in item:
            item = item[3:-4].replace('adet', '').split()
            content = clear_split_string(item)
            # print(content[0] + "  " + content[1]+" adet    "+content[2])
            Food.objects.update_or_create(name=content[0], calorie=content[2], unit_amount=content[1],
                                          measurement_unit="adet")

        elif "dilim" in item:
            item = item[3:-4].replace('dilim', '').split()
            content = clear_split_string(item)
            content[1] = "1"
            # print(content[0] + "  " + content[1]+" dilim    "+content[2])
            Food.objects.update_or_create(name=content[0], calorie=content[2], unit_amount=content[1],
                                          measurement_unit="dilim")
        else:
            pass
    print(len(all_items))
    print(len(all_items_as_string))

