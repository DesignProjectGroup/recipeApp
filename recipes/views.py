# from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from recipes.models import Food, Recipe, Ingredient, MeasureTable
import os
from math import*


selected_food = []
def list_recipes(request):
   return render(request, 'recipes/suggested_recipes.html', {})


def call_functions(request):
    # get_all_recipes()
    # calculate_calories()
    suggestion_recipe(request)
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
                print(i)
                parse_ingredient_list = parse_ingredient(i)
                print(parse_ingredient_list)
                Ingredient.objects.update_or_create(name=parse_ingredient_list[2],
                                                    count=parse_ingredient_list[0],
                                                    measurementUnit=parse_ingredient_list[1],
                                                    subtitle=ingredients_subtitles_text_list
                                                    [ingredients_subtitle_number],
                                                    recipe=this_recipe)
# Seda
# Adds measure and their grams in the MeasureTable
def get_measure():
    cwd = os.path.realpath("measure_table.txt")  # find measure.txt path in the project
    data = [i.strip('\n').split('\t') for i in open(cwd)]  # open and split measure.txt
    for m in range(0, len(data)):
        if(data[m][2]):
            # Adds data to the MeasureTable
            MeasureTable.objects.update_or_create(name=data[m][0],
                                                  object_type=data[m][1],
                                                  technical_measure=data[m][2])


# Seda
# Splitting materials by measure and name
def parse_ingredient(ingredientString):
    parse_ingredient_list = [] # keeps the materials after the parsing
    # measures ölçüleri tutuyor ekleme yapılabilir
    measures = ['yemek kaşığı', 'çay kaşığı', 'tatlı kaşığı', 'su bardağı', 'çay bardağı', 'kahve fincanı',
                'fincan', 'bardak', 'kaşık', 'gram', 'adet', 'tane', 'diş', 'demet', 'tutam', 'dilim', 'avuç',
                'gr.', 'paket', 'litre', 'ml.', 'bağ', 'damla']
    for measure in measures:
        if measure in ingredientString:
            ingredient = ingredientString.split(measure)
            parse_ingredient_list.append(ingredient[0])
            parse_ingredient_list.append(measure)
            parse_ingredient_list.append(ingredient[1])
            break
    else: # eğer ölçü yoksa sadece malzeme adı varsa
        if ingredientString not in parse_ingredient_list:
            parse_ingredient_list.append("")
            parse_ingredient_list.append("")
            parse_ingredient_list.append(ingredientString)
    return parse_ingredient_list


# Seda
# Returns similarity of two list
def jaccard_similarity(x, y):
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality/float(union_cardinality)


# Seda
# Returns the intersection of two lists
def jaccard_similarity_list(x, y):
    intersection_cardinality = set.intersection(*[set(x), set(y)])
    return intersection_cardinality


# Seda
# Finds recipes containing the all entered ingredients or the greatest similarity of some of the entered ingredients
def suggestion_recipe(request):
    ing = ['Orta boy patates', 'Tuz', 'Karabiber', 'Kuru nane']
    recipe_list = []  # keeps suggestion recipes
    missing_recipe = {}  # keeps suggestion recipes that ingredients are missing
    matching_list = []
    missing_ingredient = 0
    for i in range(0, len(ing)):
        if Ingredient.objects.filter(name=ing[i]).exists():  # Check  ingredient in Ingredient table
            ingredients = Ingredient.objects.filter(name=ing[i])  # Get ingredient object in Ingredient query
            for ingredient in ingredients:
                matching_ingredient = Ingredient.objects.filter(recipe__id=ingredient.recipe.id)
                matching_list = matching_ingredient.values_list('name', flat=True)
                # matching_ingredient : holds Ingredient objects with the same recipe id as the ingredient
                # matching_list : keeps all ingredient names that have the same recipe id
                x = 0
                for match in matching_ingredient:
                    for j in range(0, len(ing)):
                        if match.name == ing[j]:
                            x += 1
                if(x == len(matching_list)):  # If a recipe contains all the ingredients entered
                    recipe_list.append(ingredient)
                    missing_ingredient = jaccard_similarity(ing, matching_list)

                # If the jaccard_similarity of items entered and  ingredients of recipe are greater than the previous jaccard_similarity, suggestion recipe changes
                elif(missing_ingredient < jaccard_similarity(ing, matching_list)):
                    missing_ingredient = jaccard_similarity(ing, matching_list)
                    missing_recipe.clear()
                    missing_recipe[ingredient] = set(matching_list)- set(jaccard_similarity_list(ing, matching_list))
                elif (ingredient not in missing_recipe and missing_ingredient == jaccard_similarity(ing, matching_list)):
                    missing_recipe[ingredient] = set(matching_list) - set(jaccard_similarity_list(ing, matching_list))

    # If there is no recipe containing all ingredients entered
    if(len(recipe_list) == 0):
        for x, y in missing_recipe.items():
            print(x.recipe.title, "\t", y)
    else:
        for r in recipe_list:
            print(r.recipe.title)
