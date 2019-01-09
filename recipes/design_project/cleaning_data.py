import ast
import json

import inline as inline
import matplotlib
from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd
import re


def get_links_in_Links(url):
    r = requests.get(url)
    data = r.text
    more_links = []
    soup = BeautifulSoup(data, "html.parser")
    data = soup.findAll('ul', attrs={'class': '_1JZtFzRChr9o1znj9XH77d'})
    for div in data:
        links = div.findAll('a')
        for a in links:
            more_links.append("https://yemek.com" + a['href'])
    return more_links


def get_main_links():
    url = "https://yemek.com/tarif/"
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    tags = soup.find_all('a')
    links = []
    for tag in tags:
        link = str(tag.get('href'))
        if "tarif" in link:
            links.append(link)
    return list(set(links))


# save data from yemek.com
def save_data_in_csv_file(combine_all_data_in_list):
    with open('Dataset.csv', 'a', newline='\n') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(combine_all_data_in_list)


def save_total_data(recipe_name, number_of_ingerdients, num_preparation_words, cooking_time,ingredients,preparation,label):
    combine_all_inputs = [recipe_name, number_of_ingerdients, num_preparation_words, cooking_time,ingredients,preparation,label]
    print(combine_all_inputs)
    with open('labeled_dataset.csv', 'a', newline='\n') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(combine_all_inputs)


def extract_data_from_all_links(all_links):
    for i in range(len(all_links)):
        r = requests.get(all_links[i])
        soup = BeautifulSoup(r.content, "html.parser")
        all_categories = soup.find_all("div", attrs={"class": "col-md-12"})
        name_of_recipe = ""
        cooking_time = []
        malzemeler = ""
        how_to_cook = []
        for categories in all_categories:
            # just to get the name of recipe
            name = soup.select('h1._24TExulPZfGpRqfeteo1wi')[0].text.strip()
            if not name_of_recipe:
                name_of_recipe = name

            # HAZIRLAMA SÜRESİ
            hazirlama_sursi = categories.find_all('div', {'class': '_1BBirJtLpT2N1duIC5E3cG'})
            for res in hazirlama_sursi:
                if res.text not in cooking_time:
                    cooking_time.append(res.text)
                # print(res.text)

            # Malzemeler
            Malzeme = categories.find_all('div', {'class': '_1GGPkHIiaumnRMT-S1cU29'})
            for res in Malzeme:
                if res.text not in malzemeler:
                    malzemeler = malzemeler + res.text + ","
                # print(res.text)
            # Nasıl Yapılır?
            nasil_yapilar = categories.find_all('ol', {'class': '_3Z2MUIzzMNhESoosDGuUqN'})
            for res in nasil_yapilar:
                # print(res.text)
                how_to_cook.append(res.text)
        print(i)
        print(name_of_recipe)
        print(cooking_time)
        print(malzemeler)
        print(how_to_cook)
        print(all_links[i])
        print("\n\n")
        combine_all_data_in_list = [name_of_recipe, cooking_time[1][16:], cooking_time[2][14:], len(malzemeler),
                                    malzemeler, how_to_cook[0], all_links[i]]
        print(combine_all_data_in_list)
        save_data_in_csv_file(combine_all_data_in_list)


def extract_more_links_from_main_links(main_links):
    all_links = []
    for i in range(len(main_links)):
        more_links = get_links_in_Links(main_links[i])
        for j in range(len(more_links)):
            all_links.append(more_links[j])
        # print(main_links)
    return list(set(all_links))


def add_colomn_names():
    df = pd.read_csv('labeled_dataset.csv', header=None)
    df.rename(
        columns={0: 'recipe_name', 1: 'number_of_ingerdients', 2: 'number_of_preparation_words', 3: 'cooking_time',4:"ingredients", 5: "preparation:",6:"label"},
        inplace=True)
    df.to_csv('labeled_datasetFinal.csv', index=False)  # save to new csv file


def prepocessing_scraped_data():
    data = pd.read_csv('data.csv')
    name_of_recipe = data['recipe'].values
    malzemeler = data['Malzemeler'].values.tolist()
    cooking_times = data['cooking_time']
    preparation_words_number = data['Nasıl Yapılır?'].str.lower().str.split()

    ingredient = data['Malzemeler'].values.tolist()

    for j in range(len(data)):
        recipe_name = name_of_recipe[j]
        number_of_ingerdients = len(ast.literal_eval(ingredient[j]))
        preparation = len(preparation_words_number[j])
        cooking_time = cooking_times[j]
        combine_all_inputs = [recipe_name, number_of_ingerdients, preparation, cooking_time]
        save_total_data(combine_all_inputs[0], combine_all_inputs[1], combine_all_inputs[2], combine_all_inputs[3])


def read_json_file(filename):
    # with open("all_recipes .json") as jf:
    #     data = json.load(jf)
    #     for p in data['title']:
    #         print(p)
    # all_recipes
    # with open('all_recipes .json', 'r') as jf:
    counter = 0
    total2_of_words=0
    counter2=0


    with open(filename, 'r') as jf:
        all_data = json.load(jf)
    print(len(all_data))
    for recipe in all_data:
        recipe_name = recipe["title"]
        # print(recipe["isHard"])

        # label data as hard or easy
        label=""
        if recipe['isHard'] == "USTA İŞİ":
            label = "hard"
        elif recipe['isHard']== "ORTA ZORLUKTA":
            label ="hard"

        else:
            label +="easy"
        print(label)

        # preparation, we need to get number of words that describe the recipe
        preparation = ""
        describtion=""
        for x in recipe['preparation']:
            preparation = preparation + x['name']
        describtion=preparation
        preparation = preparation.split()

        # extract cooking time.
        cooking_time = recipe['time']
        cooking_time = cooking_time.split()

        time = 0
        if cooking_time[0] == "30-60":
            time = 45
        elif cooking_time[0] == "30":
            time = 30
        elif cooking_time[0] == "60+":
            time = 70
        else:
            time = 0


        # number_of_ingerdients, we need to getnumber of ingerdients that describe the recipe
        number_of_ingerdients = len(recipe['ingredients'])
        ingredients=[]
        for x in recipe['ingredients']:
            ingredients.append(x['name'])
        print(describtion)

        number_of_ingerdients = len(recipe['ingredients'])
        # print("number_of_ingerdients",number_of_ingerdients)

        save_total_data(recipe_name, number_of_ingerdients, len(preparation), time,ingredients,describtion,label)



def save_link_in_csv(all_links):
    with open('recipe_links.csv', 'a', newline='\n') as f:
        for link in all_links:
            f.write(link)
            f.write('\n')


def main_functions():
    # # get all links from yemek.com and store them in this list
    # all_links = []
    # with open('recipe_links.csv', 'r') as f:
    #     reader = csv.reader(f)
    #     links = list(reader)
    #     for link in links:
    #         all_links.append(link[0])
    #
    # print(len(all_links))
    # all_links = extract_more_links_from_main_links(all_links)
    #
    # # give me all data about recipe such as : name, time for preparation, time for cooking, contents, how to cook and the link
    # # save all data in csv file
    #
    # extract_data_from_all_links(all_links)

    # prepocessing_scraped_data()

    read_json_file("recipes_3522.json")
    read_json_file("recipes1204.json")
    add_colomn_names()


main_functions()
