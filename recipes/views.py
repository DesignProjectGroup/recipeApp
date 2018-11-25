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
    get_all_recipes()
    #calculate_calories()
    getLinks_from_trendus()
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
                'gr.', 'paket', 'litre']
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


#mohammed
def clear_split_string(item):
    if len(item) == 4:
        item[0] = item[0] + " " + item[1]
        del item[1]
    elif len(item) == 5:
        item[0] = item[0] + " " + item[1] + " " + item[2]
        del item[1]
        del item[2]
    return item


#mohammed
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


