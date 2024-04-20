UNITS = {'tbsp', 'tsp', 'cm', 'g', 'cup', 'cups', 'mL', 'handful', 'pinch', 'slices', 'can', 'bag'}


def url_to_dish(url):
    words = url.split('.')[0].split('-')
    return ' '.join([w.capitalize() for w in words])


def format_ingredients(txt):
    ingredients = []
    for line in txt.split('\n'):
        words = line.split()
        ingredient = {'number': words[0]}
        if words[1] in UNITS:
            ingredient['unit'] = words[1]
            residual = ' '.join(words[2:])
        else:
            ingredient['unit'] = ''
            residual = ' '.join(words[1:])
        if ' (' in residual:
            ingredient['item'] = residual.split(' (')[0]
            ingredient['details'] = residual.split(' (')[1].split(')')[0]
        else:
            ingredient['item'] = residual
            ingredient['details'] = ''
        ingredients.append(ingredient)
    return ingredients


def format_steps(txt):
    steps = []
    for line in txt.split('\n'):
        if line[0].isdigit():
            continue
        steps.append(line)
    return steps

