# from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from recipes.models import Food, Recipe, Ingredient, MeasureTable
import os
from django.shortcuts import redirect
from .forms import UserProduct
from urllib.request import urlopen, Request
from collections import Counter
from operator import itemgetter
selected_food = []


def get_recipe_page(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    ingredients = Ingredient.objects.filter(recipe__id=recipe.pk)
    return render(request, 'recipes/recipe_page.html', {'recipe': recipe, 'ingredients': ingredients})


# malzeme seçildikten sonra tarif öner
def list_recipes(request):
    form = UserProduct(request.POST)
    if form.is_valid():
        user_products = form.cleaned_data.get('userProducts')
        selected_food.clear()
        selected_food.extend(user_products)
        all_suggestion_recipes = suggestion_recipe()

        return render(request, 'recipes/suggested_recipes.html', {'selected_food': selected_food,
                                                                  'all_suggestion_recipes': all_suggestion_recipes})


# kullanıcıya malzeme seçtir
def select_ingredients(request):
    form = UserProduct()
    return render(request, 'recipes/home_page.html', {'form': form, 'selected_food': selected_food})


# recipes ve ingredients table ları güncelle
def create_recipes_db(request):
    if 'new_recipe_btn' in request.GET:
        get_all_recipes()
        return redirect('/manager_page')
    elif 'new_ingredient_btn' in request.GET:
        read_food_calories("food_calories.txt")
        get_measure()
        return redirect('/manager_page')
    return render(request, 'recipes/manager_page.html', {})


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
        img = p.find("img")
        if img is not None:
            try:
                img_link = img["srcset"].split(",")[0].split(" ")[0]
            except KeyError:
                img_link = ""
                continue
        if not p.text == "":
            recipe_preparation_steps_list = recipe_preparation_steps_list + p.text + "\n"

    Recipe.objects.update_or_create(title=recipe_title, text=recipe_preparation_steps_list, image=img_link)
    this_recipe = Recipe.objects.get(title=recipe_title, text=recipe_preparation_steps_list, image=img_link)

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

                parse_ingredient_list = parse_ingredient(i)
                product_name = parse_ingredient_list[2].strip()
                product_count = parse_ingredient_list[0].strip()
                product_measurement_unit = parse_ingredient_list[1].strip()
                # print(this_recipe.title)
                calorie = calculate_ingredient_calories(product_name, product_measurement_unit, product_count)
                Ingredient.objects.update_or_create(name=product_name,
                                                    count=product_count,
                                                    measurementUnit=product_measurement_unit,
                                                    subtitle=ingredients_subtitles_text_list
                                                    [ingredients_subtitle_number],
                                                    recipe=this_recipe, calorie=calorie)


# Seda
# Adds measure and their grams in the MeasureTable
# Nohut	Su Bardağı	170 gram
# tüm besinlerin belirlenen ölçüm aleti ile kaç grama denk geldiğini hesaplar.
def get_measure():
    cwd = os.path.realpath("measure_table.txt")  # find measure.txt path in the project
    data = [i.strip('\n').split('\t') for i in open(cwd)]  # open and split measure.txt
    for m in range(0, len(data)):
        # print(data[m])
        if data[m][2]:
            # Adds data to the MeasureTable
            MeasureTable.objects.update_or_create(name=data[m][0],
                                                  object_type=data[m][1],
                                                  technical_measure=data[m][2], measurementUnit="gram")


# Seda
# Splitting materials by measure and name
# "1 çay kaşığı kekik" gibi içeriği parse eder ve parse_ingredient_list 'e atar
def parse_ingredient(ingredient_string):
    # keeps the materials after the parsing
    parse_ingredient_list = []
    # measures ölçüleri tutuyor ekleme yapılabilir
    measures = ['yemek kaşığı', 'çay kaşığı', 'tatlı kaşığı', 'su bardağı', 'çay bardağı', 'kahve fincanı',
                'fincan', 'bardak', 'kaşık', 'gram', 'adet', 'tane', 'diş', 'demet', 'tutam', 'dilim', 'avuç',
                'gr.', 'paket', 'litre', 'bağ', 'damla']
    for measure in measures:
        if measure in ingredient_string:
            ingredient = ingredient_string.split(measure)
            parse_ingredient_list.append(ingredient[0])
            parse_ingredient_list.append(measure)
            parse_ingredient_list.append(ingredient[1])
            break
    # eğer ölçü yoksa sadece malzeme adı varsa
    else:
        if ingredient_string not in parse_ingredient_list:
            parse_ingredient_list.append("")
            parse_ingredient_list.append("")
            parse_ingredient_list.append(ingredient_string)
    return parse_ingredient_list


# food_calories.txt file'ı parse eder ve Food table'a ekler.
# food_calories.txt dosyası "Et Suyu Çorbası	1	porsiyon	35" verisini tutar
# food_calories.txt veriyi bu dosyadan alıp measure_table.txtde gram cinsini bulup ve yine food_calories.txt de
# calorie karşılığına göre calorisi hesaplanır
def read_food_calories(food_calories_file):
    file = open(food_calories_file, "r")
    line = file.readline()

    while line:
        split_line = line.split("\t")
        # print(split_line)
        split_line[3] = split_line[3].replace("\n", "")
        Food.objects.update_or_create(name=split_line[0], count=split_line[1], measurementUnit=split_line[2],
                                      calorie=split_line[3])
        line = file.readline()


#
def clean_product_name(name):
    foods_name_list = MeasureTable.objects.values_list('name', flat=True).distinct()
    match_amount = 0
    clean_name = "*"
    for f in foods_name_list:
        if f.lower() in name.lower():
            parsed_f = f.split(" ")
            m = len(parsed_f)
            if m > match_amount:
                match_amount = m
                clean_name = f
    if clean_name == "*":
        print(name)
    return clean_name


# ingredients tabledaki calorie attributunu bu fonksiyonu kullanarak dolduruyoruz.
def calculate_ingredient_calories(name, measurement_unit, count):
    try:
        m0 = MeasureTable.objects.get(name=name, object_type=measurement_unit)
    except MeasureTable.DoesNotExist:
        m0 = None
    if m0 is None:
        if measurement_unit != "":
            clean_name = clean_product_name(name)
        else:
            clean_name = name
    else:
        clean_name = name
    if measurement_unit == "gr.":
        measurement_unit = "gram"
    calorie = 0
    m = None
    f = None
    try:
        m = MeasureTable.objects.get(name=clean_name, object_type=measurement_unit)
    except MeasureTable.DoesNotExist:
        if measurement_unit != "":
            print("----measure_table.txt'ye ekle:-----")
            print(clean_name, end=" -- ")
            print(measurement_unit)
        m = None
    if m is not None:
        try:
            f = Food.objects.filter(name=clean_name, measurementUnit=m.measurementUnit)
        except Food.DoesNotExist:
            # print("----food_calories.txt'ye ekle:-----")
            # print(clean_name)
            f = None
    if m is None:
        if f is None:
            if measurement_unit == "":
                calorie = 0
        else:
            calorie = m.technical_measure * f.calorie / f.count * count
    return calorie


# Seda
# Returns similarity of two list
def jaccard_similarity(x, y):
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality / float(union_cardinality)


# Seda
# Returns the intersection of two lists
def intersection_list(x, y):
    intersection_cardinality = set.intersection(*[set(x), set(y)])
    return intersection_cardinality


# Seda
# Finds recipes containing the all entered ingredients or the greatest similarity of some of the entered ingredients
# kullanıcı ürün girdikten sonra kullanıcıya tarif gösterir.
def suggestion_recipe():
    most_used()
    all_suggestion_recipes = []
    matching_list = []
    ingredient_title = []
    l = []
    for i in range(0, len(selected_food)):
        if Ingredient.objects.filter(name=selected_food[i]).exists():  # Check ingredient in Ingredient table
            ingredients = Ingredient.objects.filter(name=selected_food[i])  # Get ingredient object in Ingredient query
            for ingredient in ingredients:
                recipe_list = []  # keeps suggestion recipes
                matching_ingredient = Ingredient.objects.filter(recipe__id=ingredient.recipe.id)
                matching_list = matching_ingredient.values_list('name', flat=True)
                # matching_ingredient : holds Ingredient objects with the same recipe id as the ingredient
                # matching_list : keeps all ingredient names that have the same recipe id
                x = 0
                for match in matching_ingredient:
                    name = match.name
                    for j in range(0, len(selected_food)):
                        name = clean_product_name(name)
                        if name.lower() == selected_food[j].lower():
                            x += 1
                if ingredient.recipe.title not in ingredient_title:
                    ingredient_title.append(ingredient.recipe.title)
                    recipe_list.append(ingredient.recipe.title)
                    if x == len(matching_list):  # If a recipe contains all the ingredients entered
                        recipe_list.append("")
                    else:
                        recipe_list.append(set([y.lower() for y in matching_list]) -
                                           set(intersection_list([x.lower() for x in selected_food],
                                                                 [y.lower() for y in matching_list])))
                    recipe_list.append(ingredient.recipe.pk)
                    intersect_products = intersection_list([x.lower() for x in selected_food],
                                                                 [y.lower() for y in matching_list])
                    recipe_list.append(list(intersect_products))
                    all_suggestion_recipes.append(recipe_list)
    return all_suggestion_recipes


# Seda
# Finds intersecting ingredients in recipes that have selected_food ingredient.
def most_used():
    most_common = {}  # Keeps intersecting ingredients from recipes that have selected_food ingredients
    recipe_list = {}  # Keeps recipes of the having a maximum number of intersections ingredients with selected_food
    common = []  # Keeps intersecting ingredients
    intersection_recipe = []
    ingredient_title = []
    # Finds recipes of the having a maximum number of intersections ingredients with selected_food
    for i in range(0, len(selected_food)):
        intersection = []
        if Ingredient.objects.filter(name=selected_food[i]).exists():  # Check ingredient in Ingredient table
            ingredients = Ingredient.objects.filter(name=selected_food[i])  # Get ingredient object in Ingredient query
            for ingredient in ingredients:
                matching_ingredient = Ingredient.objects.filter(recipe__id=ingredient.recipe.id)
                matching_list = matching_ingredient.values_list('name', flat=True)
                intersection = intersection_list([x.lower() for x in selected_food],
                                                       [y.lower() for y in matching_list])

                if ingredient.recipe.title not in ingredient_title:
                    c = ', '.join(intersection)
                    if c not in recipe_list.keys():
                        recipe_list[c] = []
                    else:
                        if len(list(common)) < len(list(intersection)):
                            common = intersection
                            ingredient_title = []
                            ingredient_title.append(ingredient.recipe.title)
                            recipe_list = {}
                            recipe_list[c] = []
                            recipe_list[c].append(ingredient)
                        elif len(list(common)) == len(list(intersection)):
                            common = intersection
                            ingredient_title.append(ingredient.recipe.title)
                            recipe_list[c].append(ingredient)

    # Finds intersecting ingredients in recipes that have selected_food ingredient
    for key, value in recipe_list.items():
        ingredient_list = []
        if len(value) > 1:
            for val in list(value):
                ingredients = Ingredient.objects.filter(recipe_id=val.recipe.id)
                matching_list = ingredients.values_list('name', flat=True)
                if len(ingredient_list) == 0:
                    ingredient_list = matching_list
                else:
                    intersections = intersection_list([x.lower() for x in ingredient_list],
                                                      [y.lower() for y in matching_list])

                    keys = key.split(', ')
                    if len(list(intersection_recipe)) < len(list(intersections)):
                        intersection_recipe = intersections
                        most_common[key] = []
                        not_intersect = list(intersection_recipe - set(keys))
                        most_common[key] = not_intersect
                    elif len(list(ingredient_list)) == len(list(intersections)):
                        intersection_recipe = intersections
                        not_intersect = list(intersection_recipe - set(keys))
                        most_common[key].append(not_intersect)

    return most_common
