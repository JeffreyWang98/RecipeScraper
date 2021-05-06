import scrapy
import json
from genius_kitchen_parser import *

class ChefSpider(scrapy.Spider):
    name = 'chefspider'
    allowed_domains = ['geniuskitchen.com']
    start_urls = ['https://www.geniuskitchen.com/recipe/carrot-bread-27757']
    AUTOTHROTTLE_ENABLED = True
    AUTOTHROTTLE_START_DELAY = 1

    def find_id(self, url):
        '''Extract the recipe id from the URL
        '''
        i = url.rfind('#')
        if i != -1: # has fragment identifier
            url = url[:i]
        return int(url[url.rfind('-') + 1:])

    def parse(self, response):
        '''Parses a recipe webpage with BeautifulSoup
        Ignores page if it's not a recipe webpage
        Proceeds to web crawl and parse all related pages
        '''
        # TODO change this to scrapy if possible
        # TODO the generic recipe page https://www.geniuskitchen.com/recipe/
        # will still be recognized for parsing when it shouldn't
        # TODO check for duplicates and stop before parsing
        url = response.url

        if url.startswith('https://www.geniuskitchen.com/recipe/'):
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')

            recipe = parse_recipe(soup)
            recipe.id = self.find_id(url)
            recipe.url = url

            # save data to json
            file = open(str(recipe.id) + '.json', 'w')
            output = {str(recipe.id): {'recipe_name': recipe.name, 'recipe_url': recipe.url, 'recipe_ingredients': recipe.json_ing(), 'recipe_steps': recipe.json_steps()}}
            json.dump(output, file)
            file.close()

            # display data for debugging
            print(recipe.name)
            for section in recipe.ing_sections:
                print(section.name)
                for i in section.ingredients:
                    print(i.quantity, '|', i.measurement, '|', i.ingredient, '|', i.details)
        
        # start crawling
        for link in response.xpath('//a/@href').extract():
            yield response.follow(link, callback=self.parse)

        ### uses scrapy xpath
        # recipe = Recipe()
        # recipe.name = response.xpath('//h1/text()').extract_first()
        
        # ing_list = response.xpath("//ul[@class='ingredient-list']/*")

        # for line in ing_list:
        #     self.log(line.extract())

        # page = response.url.split("/")[-2]
        # filename = 'recipe-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
