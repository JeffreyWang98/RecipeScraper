#
# Parse recipes from html on geniuskitchen.com
# 
import scrapy
import pandas as pd
import requests
from bs4 import BeautifulSoup

class Recipe:
    def __init__(self, name='', id=0, url=''):
        self.name = name
        self.id = id
        self.url = url
        self.ing_sections = []
        self.step_sections = []

    def json_ing(self):
        all_sections = []
        for section in self.ing_sections:
            sec = []
            for i in section.ingredients:
                sec.append({'ingredient': {'quantity': i.quantity, 'measurement': i.measurement, 'name': i.ingredient, 'details': i.details}})
            all_sections.append({'ingredients_section': {'section_name': section.name, 'ingredients': sec}})
        return all_sections

    def json_steps(self):
        all_sections = []
        for section in self.step_sections:
            all_sections.append({'steps_section': {'name': section.name, 'steps': section.steps}})
        return all_sections

class Ingredient:
    def __init__(self, qty, qty_type, ing, details):
        self.quantity = qty.strip()
        self.measurement = qty_type.strip()
        self.ingredient = ing.strip()
        self.details = details.strip()

# Ingredient sections for recipes with multiple parts
class IngredientSection:
    def __init__(self, name):
        self.name = name
        self.ingredients = []

    def add_ingredient(self, qty, qty_type, ing, details):
        self.ingredients.append(Ingredient(qty, qty_type, ing, details))

class StepsSection:
    def __init__(self, name):
        self.name = name
        self.steps = []
    
    def add_step(self, step):
        self.steps.append(step.strip())

def remove_tags(to_remove, lst):
    '''Remove specified tags in a soup
    '''
    for tag in to_remove:
        for match in lst.find_all(tag):
            match.unwrap()

def parse_recipe(soup):
    # Find recipe name
    recipe_header = soup.find(class_='recipe-header')
    recipe_header = recipe_header.find_all('h1')
    recipe = Recipe(recipe_header[0].contents[0])

    # Find ingredients by section
    ing_list_items = soup.find(class_='ingredient-list')
    ing_list_items = ing_list_items.find_all('li')
    sections = []
    section = None

    # Iterate through each section/ingredient item
    for item in ing_list_items:
        # Assumes class is 'ingredient-section'
        if item.has_attr('class'):
            if section != None: # not first section
                sections.append(section)
            section = IngredientSection(item.contents[0].contents[0])
        else:
            if section == None:
                section = IngredientSection('')
            qty, qty_type, ing, details = parse_ingredients(item)
            section.add_ingredient(qty, qty_type, ing, details)

    # Add last section
    sections.append(section)
    recipe.ing_sections = sections

    # Find directions by section
    dir_list_items = soup.find(class_='directions-inner container-xs')
    dir_list_items = dir_list_items.find_all('li')
    sections = []
    section = None

    # Iterate through each section/ingredient item
    for item in dir_list_items[:-1]:
        # Assumes class is 'direction-section'
        if item.has_attr('class'):
            if section != None: # not first section
                sections.append(section)
            section = StepsSection(item.contents[0])
        else:
            if section == None:
                section = StepsSection('')
            section.add_step(item.contents[0])
    
    # Add last section
    sections.append(section)
    recipe.step_sections = sections

    return recipe

def parse_ingredients(ing):
    quantity = quantity_type = ingredient = extra = ''

    ### Quantity
    qty_tags = ing.find(class_='qty')
    remove_tags(['sup', 'sub'], qty_tags)

    # Concatenate quantity (fractions)
    for match in qty_tags.contents:
        quantity += str(match)
        
    ### Unit of measurement, ingredient
    food_tags = ing.find(class_='food')

    for index, item in enumerate(food_tags.contents):
        if index == 0:
            item = item.strip()
            if ' ' not in item:
                # only has measurement
                quantity_type = item
            elif ' ' in item and quantity == '':
                # only has ingredient
                ingredient = item.strip()
            else:
                # has measurement and ingredient
                quantity_type, ingredient = item.split(maxsplit=1)
                ingredient += ' '
        elif index == 1:
            ingredient += item.contents[0]
        else:
            extra += item.strip() + ' '

    return quantity, quantity_type, ingredient, extra

def main():
    # Create a BeautifulSoup object from site
    page = requests.get('https://www.geniuskitchen.com/recipe/carrot-bread-27757')
    # page = requests.get('https://www.geniuskitchen.com/recipe/tsr-version-of-starbucks-pumpkin-scones-by-todd-wilbur-214051')
    # page = requests.get('https://www.geniuskitchen.com/recipe/linguine-with-sausage-and-kale-74821')
    # page = requests.get('https://www.geniuskitchen.com/recipe/best-banana-bread-2886')
    soup = BeautifulSoup(page.text, 'html.parser')

    recipe = parse_recipe(soup)
    for i in recipe.ing_sections:
        print(i.name)
        for j in i.ingredients:
            print(j.quantity, '|', j.measurement, '|', j.ingredient, '|', j.details)

    for i in recipe.step_sections:
        print(i.name)
        for j in i.steps:
            print(j)

if __name__ == "__main__":
    main()

# read whole ingredient line
# use parsing to detect "cup, teaspoon, tablespoon, ..."
# use parsing to detect "finely grated, chopped, ..."
# split the number, measurement unit, description, and ingredient
# parse things with "or"