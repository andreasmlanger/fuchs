from django.shortcuts import render
from main.airtable_data import get_airtable
from main.utils import get_avatar
from .utils import *


def index(request, url=None):
    airtable = get_airtable('COOKBOOK')
    records = airtable.get_all(sort='Dish')
    if url:
        dish_name = url_to_dish(url)
        dish = [r['fields'] for r in records if r['fields']['Dish'] == dish_name][0]
        ingredients = format_ingredients(dish['Ingredients'])
        steps = format_steps(dish['Steps'])
        dishes = [(dish['Dish'], dish['Image'][0]['url'])]
        d = {'ingredients': ingredients, 'steps': steps, 'dishes': dishes}
    else:
        dishes = [(r['fields']['Dish'], r['fields']['Image'][0]['url']) for r in records]
        d = {'dishes': dishes}
    return render(request, 'cookbook/index.html', d | {'avatar': get_avatar(request)})
