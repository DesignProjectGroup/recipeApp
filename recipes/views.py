# from django.shortcuts import render
#  -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from recipes.models import Food, Recipe, Ingredient, MeasureTable
from comments.models import Comment
import os
from django.shortcuts import redirect
from .forms import UserProduct
from urllib.request import urlopen
from django.core.files.temp import NamedTemporaryFile
import urllib
from urllib.parse import urlparse
from django.core.files.base import ContentFile
from django.core.files import File
import datetime
from comments.views import read_file, do_semantic_analysis
import json
import re
import re

selected_food = []


# seçilen tarifi getir.
def get_recipe_page(request, pk):
    time = ""
    recipe = Recipe.objects.get(pk=pk)
    all_ingredients = Ingredient.objects.filter(recipe__id=recipe.pk)
    ingredients = []
    for i in all_ingredients:
        if i.count == 0.5:
            i.count = "1/2"
        elif i.count == 0.25:
            i.count = "1/4"
        elif i.count == 0.75:
            i.count = "3/4"
        elif i.count == 0:
            i.count = ""
        else:
            i.count = int(round(i.count))
        ing = [i.count, i.measurementUnit, i.name]
        ingredients.append(ing)
    if request.method == 'POST':
        time = datetime.datetime.now().date()
        text = request.POST.get('textfield', None)
        is_pos = do_semantic_analysis(text)
        Comment.objects.update_or_create(recipe=recipe, text=text, isPositive=is_pos)
    comments = Comment.objects.filter(recipe=recipe)

    return render(request, 'recipes/recipe_page.html',
                  {'calorie': round(recipe.calorie), 'recipe': recipe, 'ingredients': ingredients,
                   'comments': comments, 'time': time})


# malzeme seçildikten sonra tarif öner
def list_recipes(request):
    all_suggestion_recipes = []
    most_common = {}
    most_common_key = []
    if request.method == "GET":
        all_suggestion_recipes = suggestion_recipe()
        most_common = most_used()
        most_common_key = most_common.keys()
        if '/suggested_recipes/alphabetic_sort' in request.path:
            # old_post = request.session.get('_old_post').get('userProducts')
            all_suggestion_recipes.sort(key=lambda x: x[0])
        elif 'suggested_recipes/calorie_sort' in request.path:
            all_suggestion_recipes.sort(key=lambda x: x[4])
        elif 'suggested_recipes/easy_hard_sort' in request.path:
            all_suggestion_recipes.sort(key=lambda x: x[0])

    else:
        form = UserProduct(request.POST)
        if form.is_valid():
            user_products = form.cleaned_data.get('userProducts')
            selected_food.clear()
            selected_food.extend(user_products)
            all_suggestion_recipes = suggestion_recipe()
            most_common = most_used()
            most_common_key = most_common.keys()
            # request.session['_old_post'] = request.POST

    return render(request, 'recipes/suggested_recipes.html', {'selected_food': selected_food,
                                                              'all_suggestion_recipes': all_suggestion_recipes,
                                                              'most_common': most_common,
                                                              'most_common_key': most_common_key})


# kullanıcıya malzeme seçtir
def select_ingredients(request):
    # write_measure_table_file("ll", "ll")
    # sort_all_products("deneme3.txt")
    # read_json_file()
    form = UserProduct()
    return render(request, 'recipes/home_page.html', {'form': form, 'selected_food': selected_food})


# tarifin kalorisini hesaplar
def calculate_recipe_calorie():
    # ingredient_calories = Ingredient.objects.values('calorie')
    ingredients = Ingredient.objects.all()
    for i in ingredients:
        i.recipe.calorie = i.recipe.calorie + i.calorie
        this_recipe = Recipe.objects.get(pk=i.recipe.pk)
        this_recipe.calorie = i.recipe.calorie
        this_recipe.save()


# ***geçici***
# file ı alfabetik olarak sıralar
# measure_table.txt yi sıraladık.
def sort_all_products(file):
    all_list = []
    f = open(file, "r")
    f2 = open("deneme4.txt", "w")
    all_lines = f.read().split("\n")
    for line in all_lines:
        if "        " in line:
            line = line.replace("        ", "\t")
        # line_split = line.split("\t")
        # print(line_split)
        all_list.append(line + "\n")

    print(all_list)
    # all_list=sorted(list(set(all_list)))

    for i in all_list:
        f2.write(i)


# tariflerin bulunduğu json dosyasını okur ve tarifleri database'e atar.
def read_json_file():
    with open('all_recipes.json', 'r') as f:
        all_recipes = json.load(f)
    # calori hesapla
    # database e kaydet
    # measure.txt ekleme yap
    # train test etiketle
    # image yayınlanma sorunu varsa çöz
    #
    f = open("deneme2.txt", "w")
    malzemeler = []
    for recipe in all_recipes["all_recipes"]:
        # this_recipe = Recipe()
        try:
            title = recipe["title"]
            image = recipe["image"]
            is_hard = recipe["isHard"]
            technical_type = recipe["technical_type"]
            time = recipe["time"]
            preparation = ""
            for i in recipe["preparation"]:
                preparation = preparation + i["name"]
            # this_recipe.title = title
            # this_recipe.image = image
            # this_recipe.isHard = is_hard
            # this_recipe.technical_type = technical_type
            # this_recipe.time = time
            # this_recipe.text = preparation
            # this_recipe.save()
            # this_ingredient = Ingredient()
            for i in recipe["ingredients"]:
                i = i["name"]
                clean_measuretable(i, malzemeler)
        except KeyError:
            # this_recipe.clean()
            continue
    for m in malzemeler:
        if m[1] == "":
            f.write(m[2] + "\t" + "\t" + "111" + "\n")
        else:
            f.write(m[2] + "\t" + m[1] + "\t" + "111" + "\n")
    print(malzemeler)
    print(len(malzemeler))


# ***geçici***
# string number içeriyor mu kontrolünü yapar.
def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))


# ***geçici***
# measure_table'a veri eklemek için kullandığımız deneme2.txt dosyasında temizlik yapar.
# 1 adet çarliston biber
def clean_measuretable(i, malzemeler):
    parse_ingredient_list = parse_ingredient(i)
    if clean_product_name(parse_ingredient_list[2]) == "*":
        parse_ingredient_list[0] = ""
        # for m in malzemeler:
        #     if parse_ingredient_list[1].lower() != m[1].lower() and parse_ingredient_list[2].lower() != m[2].lower():
        if hasNumbers(parse_ingredient_list[2]) is False:
            if "yarım" not in parse_ingredient_list[2]:
                if "Yarım" not in parse_ingredient_list[2]:
                    if "için" not in parse_ingredient_list[2]:
                        if "Üzeri" not in parse_ingredient_list[2]:
                            if "malzeme" not in parse_ingredient_list[2]:
                                if parse_ingredient_list not in malzemeler:
                                    malzemeler.append(parse_ingredient_list)
    else:

        parse_ingredient_list[0] = ""
        h = MeasureTable.objects.filter(name=clean_product_name(parse_ingredient_list[2])).values_list('object_type',
                                                                                                       flat=True)
        h2 = []
        for k in h:
            h2.append(k.lower())

        if not parse_ingredient_list[1].lower() in h2:

            print(clean_product_name(parse_ingredient_list[2]))
            print(parse_ingredient_list)
            print(h2)

            # if (parse_ingredient_list[2] == "ceviz"):
            #     # print(parse_ingredient_list[2])
            #     # print(clean_product_name(parse_ingredient_list[2]))
            #     # print(parse_ingredient_list[2] + "--" + parse_ingredient_list[1])
            if hasNumbers(parse_ingredient_list[2]) is False:
                if "yarım" not in parse_ingredient_list[2]:
                    if "Yarım" not in parse_ingredient_list[2]:
                        if "için" not in parse_ingredient_list[2]:
                            if "Üzeri" not in parse_ingredient_list[2]:
                                if "malzeme" not in parse_ingredient_list[2]:
                                    if parse_ingredient_list not in malzemeler:
                                        malzemeler.append(parse_ingredient_list)


# recipes ve ingredients table ları güncelle
def create_recipes_db(request):
    if 'new_recipe_btn' in request.GET:
        get_all_recipes()
        calculate_recipe_calorie()
        read_file("comments/text_files/positives.txt")
        read_file("comments/text_files/negatives.txt")
        return redirect('/manager_page')
    elif 'new_ingredient_btn' in request.GET:
        read_food_calories("food_calories.txt")
        get_measure()
        return redirect('/manager_page')
    return render(request, 'recipes/manager_page.html', {})


# "1/4" string'i 0.25 floata dönüştürür.
def convert_from_fraction_string_to_float(fraction_string):
    float_number = 0
    if "+" in fraction_string:
        split_list = fraction_string.split("+")
        if fraction_string[1] == "1/3":
            float_number = 0.3
        elif fraction_string[1] == "1/2":
            float_number = 0.5
        elif fraction_string[1] == "1/4":
            float_number = 0.25
        elif fraction_string[1] == "3/4":
            float_number = 0.75
        float_number = int(split_list[0]) + float_number
    elif "/" in fraction_string:
        if fraction_string == "1/3":
            float_number = 0.3
        elif fraction_string == "1/2":
            float_number = 0.5
        elif fraction_string == "1/4":
            float_number = 0.25
        elif fraction_string[1] == "3/4":
            float_number = 0.75
    else:
        float_number = float(fraction_string)
    return float_number


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


def save_image_from_url(url):
    r = requests.get(url)

    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(r.content)
    img_temp.flush()
    img_file = File(img_temp)
    return img_file


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
    img_link = None
    for p in recipe_preparation_steps:
        img = p.find("img")
        if img is not None:
            try:
                img_link = img["srcset"].split(",")[0].split(" ")[0]
            except KeyError:
                img_link = None
                continue
        if not p.text == "":
            recipe_preparation_steps_list = recipe_preparation_steps_list + p.text + "\n"

    recipe = Recipe.objects.update_or_create(title=recipe_title, text=recipe_preparation_steps_list)
    if img_link is not None:
        try:
            name = urlparse(img_link).path.split('/')[-1]
            content = ContentFile(urllib.request.urlopen(img_link).read())
            recipe[0].image.save(name, content, save=True)
        except:
            print("Resim çekilemedi!")

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
                parse_ingredient_list = parse_ingredient(i)
                product_name = parse_ingredient_list[2].strip()
                if parse_ingredient_list[0].strip().split(" ")[0] != '':
                    product_count = parse_ingredient_list[0].strip().split(" ")[0]
                    if "," in product_count:
                        product_count = product_count.replace(',', '.')
                        product_count = product_count.replace(' ', '')
                    elif "½" in product_count:
                        product_count = product_count.replace("½", "0.5")
                    elif "¼" in product_count:
                        product_count = product_count.replace("¼", "0.25")
                    elif "¾" in product_count:
                        product_count = product_count.replace("¾", "0.75")
                    elif "1/2" in product_count:
                        product_count = product_count.replace("1/2", "0.5")
                    elif "1/4" in product_count:
                        product_count = product_count.replace("1/4", "0.25")
                    elif "3/4" in product_count:
                        product_count = product_count.replace("3/4", "0.75")
                    elif "1/6" in product_count:
                        product_count = product_count.replace("1/6", "0.15")
                    elif "-" in product_count:
                        product_count = product_count.split("-")[0]
                else:
                    product_count = parse_ingredient_list[0].strip()
                    if product_count == '':
                        product_count = 0.0
                product_measurement_unit = parse_ingredient_list[1].strip()
                calorie = calculate_ingredient_calories(product_name, product_measurement_unit, product_count)
                Ingredient.objects.update_or_create(name=product_name,
                                                    count=float(product_count),
                                                    measurementUnit=product_measurement_unit,
                                                    subtitle=ingredients_subtitles_text_list
                                                    [ingredients_subtitle_number],
                                                    recipe=this_recipe,
                                                    calorie=calorie)


# Seda
# Adds measure and their grams in the MeasureTable
# Nohut	Su Bardağı	170 gram
# tüm besinlerin belirlenen ölçüm aleti ile kaç grama denk geldiğini hesaplar.
def get_measure():
    MeasureTable.objects.all().delete()
    cwd = os.path.realpath("measure_table.txt")  # find measure.txt path in the project
    data = [i.strip('\n').split('\t') for i in open(cwd)]  # open and split measure.txt
    for m in range(0, len(data)):
        print(data[m])
        if data[m][2]:
            # Adds data to the MeasureTable
            MeasureTable.objects.update_or_create(name=data[m][0],
                                                  object_type=data[m][1],
                                                  technical_measure=data[m][2], measurementUnit="gram")
    # print(MeasureTable.objects.filter(name="irmik").values_list())


# Seda
# Splitting materials by measure and name
# "1 çay kaşığı kekik" gibi içeriği parse eder ve parse_ingredient_list 'e atar
def parse_ingredient(ingredient_string):
    # keeps the materials after the parsing
    parse_ingredient_list = []
    # measures ölçüleri tutuyor ekleme yapılabilir
    measures = ['kare', 'parça', 'kase', 'yemek kaşığı', 'çorba kaşığı', 'çay kaşığı', 'tatlı kaşığı', 'su bardağı',
                'çay bardağı',
                'kahve fincanı', 'fincan', 'bardak', 'kaşık', 'gram', 'adet', 'tane', 'diş', 'demet', 'tutam', 'dilim',
                'avuç',
                'gr.', 'paket', 'litre', 'bağ', 'damla', 'baget', 'dal', 'küp', 'kilo', 'kilogram', 'yaprak', 'kavanoz',
                'çimdik', 'kutu']
    for measure in measures:
        if measure in ingredient_string:
            ingredient = ingredient_string.split(measure)
            parse_ingredient_list.append(ingredient[0].strip().split("-")[0].split(" ")[-1])
            parse_ingredient_list.append(measure.strip())
            parse_ingredient_list.append(re.sub(r" ?\([^)]+\)", "", ingredient[1].strip()))

            break
    # eğer ölçü yoksa sadece malzeme adı varsa8
    else:
        if ingredient_string not in parse_ingredient_list:
            parse_ingredient_list.append("")
            parse_ingredient_list.append("")
            parse_ingredient_list.append(re.sub(r" ?\([^)]+\)", "", ingredient_string.strip()))
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
    foods_name_list = MeasureTable.objects.values_list('name', flat=True)
    match_amount = 0
    match_amount2 = 0
    clean_name = "*"
    clean_name2 = "*"
    for f in foods_name_list:
        if f.lower() in name.lower():
            parsed_f = f.split(" ")
            m = len(parsed_f)
            m2 = len(f)
            if m2 > match_amount2:
                match_amount2 = m2
                clean_name = f
                if m > match_amount:
                    match_amount = m
                    clean_name = f
    # if clean_name == "*":
    #     print(name)
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
            if clean_name == "*":
                if name != " ":
                    print(name, end=" -- ")
                    write_measure_table_file(name, measurement_unit)
            else:
                print(clean_name, end=" -- ")
                write_measure_table_file(name, measurement_unit)
            print(measurement_unit)
        m = None
    if m is not None:
        try:
            f = Food.objects.get(name=clean_name, measurementUnit=m.measurementUnit)
            # print(f)
            # calorie = m.technical_measure * f.calorie / f.count * count
            # print("*****")
            # print(calorie)
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
    elif m is not None and f is not None:
        calorie = m.technical_measure * f.calorie / f.count * float(count)
    return calorie


# measure_table.txt yi kontrol eder eğer eksik malzeme varsa gram dönüşümü
# (örneğin bir bardak kaç gram?)hariç dosyaya ekler
def write_measure_table_file(clean_name, measurement_unit):
    file = open("deneme.txt", "a+")
    i = clean_name.lower() + "\t" + measurement_unit.lower()
    print("****")
    print(i)
    print("****")
    if i in file.read():
        print(1111)
        file.write(clean_name.lower() + "\t" + measurement_unit.lower() + "\t\n")


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
    # l = []
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
                    recipe_list.append(int(round(ingredient.recipe.calorie)))
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
