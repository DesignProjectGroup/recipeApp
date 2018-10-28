# from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render


def call_functions(request):
    get_all_recipes()
    return render(request, 'recipes/all_cooking_categories.html', {})


def get_all_recipes():
    r = requests.get('https://www.nefisyemektarifleri.com/tarifler/')
    soup = BeautifulSoup(r.content, "html.parser")
    all_parent_categories = soup.find_all("div", attrs={"class": "kategori-detay"})
    for parent_category in all_parent_categories:
        parent_category_link = parent_category.find("h3").a.get("href")
        get_recipe_link(parent_category_link)


def get_recipe_link(parent_category_link):
    r = requests.get(parent_category_link)
    soup = BeautifulSoup(r.content, "html.parser")
    recipes_list = soup.find_all("div", attrs={"class": "post-title-author"})
    for recipe in recipes_list:
        recipe_link = recipe.a.get("href")
        get_recipe(recipe_link)
    next_page = soup.find("a", attrs={"class": "nextpostslink"})
    i = 0
    # while(next_page!=None ):
    while i < 9:
        next_page_link = next_page.get("href")
        r = requests.get(next_page_link)
        soup = BeautifulSoup(r.content, "html.parser")
        recipes_list = soup.find_all("div", attrs={"class": "post-title-author"})
        for recipe in recipes_list:
            recipe_link = recipe.a.get("href")
            get_recipe(recipe_link)
        next_page = soup.find("a", attrs={"class": "nextpostslink"})
        i = i+1

# recipe_ingredients_list
# recipe_ingredient_title
# recipe_preparation_title
# recipe_preparation
#
def get_recipe(recipe_link):
    recipe_ingredients_list = []
    r = requests.get(recipe_link)
    soup = BeautifulSoup(r.content, "html.parser")
    recipe_ingredient_title = soup.find("h2", attrs={"id": "malzemeler"}).text
    ingredients_list = soup.find_all("li", attrs={"itemprop": "ingredients"})
    for ing in ingredients_list:
        recipe_ingredients_list.append(ing.text)
    recipe_preparation_title = soup.find("h2", attrs={"id": "hazirlanisi"}).text
    recipe_preparation = soup.find("div", attrs={"class": "entry_content"}).ol.text
    print(recipe_preparation)
