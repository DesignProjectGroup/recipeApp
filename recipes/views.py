# from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from recipes.models import Food, Recipe, Ingredient, MeasureTable
import os

selected_food = []
def list_recipes(request):
   return render(request, 'recipes/suggested_recipes.html', {})


def call_functions(request):
    #clean_product_name("su")
    read_food_calories("food_calories.txt")
    get_measure()
    get_all_recipes()

    #calculate_calories()
    #getLinks_from_trendus()

    #calculate_ingredient_calories("pirinç","su bardağı", 2)
    #change_measurement_unit("süt","su bardağı", "1")
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

                parse_ingredient_list = parse_ingredient(i)
                product_name = parse_ingredient_list[2].strip()
                product_count = parse_ingredient_list[0].strip()
                product_measurement_unit = parse_ingredient_list[1].strip()
                #print(this_recipe.title)
                calorie = calculate_ingredient_calories(product_name,product_measurement_unit,product_count)
                Ingredient.objects.update_or_create(name=product_name,
                                                    count=product_count,
                                                    measurementUnit=product_measurement_unit,
                                                    subtitle=ingredients_subtitles_text_list
                                                    [ingredients_subtitle_number],
                                                    recipe=this_recipe, calorie=calorie)


# Seda
# Adds measure and their grams in the MeasureTable
def get_measure():
    cwd = os.path.realpath("measure_table.txt")  # find measure.txt path in the project
    data = [i.strip('\n').split('\t') for i in open(cwd)]  # open and split measure.txt
    for m in range(0, len(data)):
        #print(data[m])
        if data[m][2]:
            # Adds data to the MeasureTable
            MeasureTable.objects.update_or_create(name=data[m][0],
                                                  object_type=data[m][1],
                                                  technical_measure=data[m][2], measurementUnit="gram")


# Seda
# Splitting materials by measure and name
def parse_ingredient(ingredient_string):
    parse_ingredient_list = [] # keeps the materials after the parsing
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
    else: # eğer ölçü yoksa sadece malzeme adı varsa
        if ingredient_string not in parse_ingredient_list:
            parse_ingredient_list.append("")
            parse_ingredient_list.append("")
            parse_ingredient_list.append(ingredient_string)
    return parse_ingredient_list


#food_calories.txt file'ı parse eder ve Food table'a ekler.
def read_food_calories(food_calories_file):
    file = open(food_calories_file, "r")
    line = file.readline()
    while line:
        split_line = line.split("\t")
        split_line[3] = split_line[3].replace("\n", "")
        Food.objects.update_or_create(name=split_line[0], count=split_line[1], measurementUnit=split_line[2],
                                      calorie=split_line[3])
        line = file.readline()


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
    if clean_name=="*":
        print("++++")
        print(name)
    return clean_name


def calculate_ingredient_calories(name, measurementUnit, count):
    try:
        m0 = MeasureTable.objects.get(name=name, object_type=measurementUnit)
    except MeasureTable.DoesNotExist:
        m0 = None
    if m0  == None:
        clean_name = clean_product_name(name)
    else:
        clean_name = name

    if measurementUnit=="gr.":
        measurementUnit = "gram"
    calorie = 0
    m = None
    f = None
    try:
        m = MeasureTable.objects.get(name=clean_name, object_type=measurementUnit)
    except MeasureTable.DoesNotExist:
        print("----measure_table.txt'ye ekle:-----")
        print(clean_name,end=" -- ")
        print(measurementUnit)
        m = None
    if m!=None:
        try:
            #print("fffffff")
            #print(name)
            f = Food.objects.get(name=clean_name, measurementUnit=m.measurementUnit)
        except Food.DoesNotExist:
            print("----food_calories.txt'ye ekle:-----")
            print(clean_name)
            f = None

    if  m==None:
        if  f ==None:
            print(".")
        else:
            calorie = m.technical_measure * f.calorie / f.count * count


    return calorie
