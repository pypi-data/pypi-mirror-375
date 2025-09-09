import requests
from bs4 import BeautifulSoup
import json

def get_data(url, arr):
    
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    complete_data = soup.find('script', type='application/ld+json').get_text().strip()
    group_array = json.loads(complete_data)
    title = ''
    ingredient_list = ''
    instruction_list = ''
    
    if isinstance(group_array, dict):
        graph_list = group_array.get('@graph', [])
        if graph_list:
            for items in graph_list:
                types = items.get('@type')
                if types == 'Recipe':
                    recipe = items
                    title = recipe.get('name')
                    ingredient_list = recipe.get('recipeIngredient')
                    instruction_list = recipe.get('recipeInstructions')
        else:
            types = group_array.get('@type')
            if types == 'Recipe':
                recipe = group_array
                title = recipe.get('name')
                ingredient_list = recipe.get('recipeIngredient')
                instruction_list = recipe.get('recipeInstructions')
    else:
        
        data = group_array[0]
        title = data.get('name')
        ingredient_list = data.get('recipeIngredient')
        instruction_list = data.get('recipeInstructions')
        
    file_name = title.lower().replace(' ', '_')
    arr.append(title)
    
    arr.append('\nIngredients:')
    for i, item in enumerate(ingredient_list, start=1):
        arr.append(f'{i}. {item}')
        
    # need to figure out why I get 'None' for instructions on some when it still has 
    # 'text' attribute
    
    arr.append('\nInstructions:')
    for section in instruction_list:
        sec_name = section.get('name')
        arr.append(f'{sec_name}')
        
        
        steps = section.get('itemListElement', [])
        for i, step in enumerate(steps, start=1):
            arr.append(f'{i}. {step.get('text')}')
            
                      
    return arr, file_name