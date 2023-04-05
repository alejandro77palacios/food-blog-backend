import argparse
import re
import sqlite3

from tables import tables

data = {
    "meals": ("breakfast", "brunch", "lunch", "supper"),
    "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
    "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")
}


def process_quantity(entry, cur):
    if len(entry) == 3:
        processed_measure = process_measure(entry[1], cur)
        if processed_measure is None:
            return None
    else:
        processed_measure = ''
    processed_ingridient = process_ingredient(entry[-1], cur)
    if processed_ingridient is None:
        return None
    measure_id = cur.execute('SELECT measure_id FROM measures WHERE measure_name = ?', (processed_measure,)).fetchone()[
        0]
    ingridient_id = \
        cur.execute('SELECT ingredient_id FROM ingredients WHERE ingredient_name = ?',
                    (processed_ingridient,)).fetchone()[
            0]
    return measure_id, ingridient_id, entry[0]


def process_measure(entry, cur):
    measures = cur.execute('SELECT measure_name FROM measures').fetchall()
    measures = [measure[0] for measure in measures]
    matches = [measure for measure in measures if re.match(entry, measure, re.IGNORECASE)]
    if len(matches) == 1:
        return matches[0]
    else:
        print('The measure is not conclusive!')
        return None


def process_ingredient(entry, cur):
    ingredients = cur.execute('SELECT ingredient_name FROM ingredients').fetchall()
    ingredients = [ingredient[0] for ingredient in ingredients]
    matches = [ingredient for ingredient in ingredients if re.search(entry, ingredient, re.IGNORECASE)]
    if len(matches) == 1:
        return matches[0]
    else:
        print('The ingredient is not conclusive!')
        return None


def fill_recipies(cur, connection):
    while True:
        print('Pass the empty recipe name to exit.')
        recipe_name = input('Recipe name: ')
        if recipe_name == '':
            connection.commit()
            break
        description = input('Recipe description: ')
        cur.execute('INSERT INTO recipes VALUES (null, ?, ?)', (recipe_name, description))
        show_meals(cur)
        meals_num = input('When the dish can be served: ').split()
        while True:
            entry = input('Input quantity of ingredient <press enter to stop>:').split()
            if entry == '' or entry == [] or entry == [''] or entry == [' '] or entry == ' ':
                connection.commit()
                break
            processed_entry = process_quantity(entry, cur)
            if processed_entry is None:
                continue
            else:
                measure_id, ingridient_id, quantity = processed_entry
                cur.execute('INSERT INTO quantity VALUES (null, ?, ?, ?, ?)',
                            (measure_id, ingridient_id, quantity, cur.lastrowid))
        for meal_num in meals_num:
            cur.execute('INSERT INTO serve VALUES (null, ?, ?)', (cur.lastrowid, meal_num))


def show_meals(cur):
    meals = cur.execute('SELECT * FROM meals').fetchall()
    for meal in meals:
        print(f'{meal[0]}) {meal[1]}', end=' ')


def get_id_recipes_for_meal(meal, cur):
    """
    Returns the recipes id of recipes in meal
    """
    query = f"SELECT meal_id FROM meals WHERE meal_name = '{meal}'"
    ids = cur.execute(query).fetchall()
    return [id[0] for id in ids]


def format_several(*entries):
    entries = [f"'{entry}'" for entry in entries]
    return '(' + ', '.join(entries) + ')'


def get_id_ingredients(cur, *ingredients):
    formatted = format_several(*ingredients)
    query = f"SELECT ingredient_id FROM ingredients WHERE ingredient_name IN {formatted}"
    ids = cur.execute(query).fetchall()
    return [id[0] for id in ids]


def get_id_recipes_with_all_ingredients(cur, *ingredients):
    num_ingredients = len(ingredients)
    id_ingredients = get_id_ingredients(cur, *ingredients)
    id_ingredients = [str(i) for i in id_ingredients]
    formatted = '(' + ', '.join(id_ingredients) + ')'
    query = f"""
    select recipe_id
    from (SELECT recipe_id, COUNT(*) as count
                          FROM quantity
                          WHERE ingredient_id IN {formatted}
                          GROUP BY recipe_id) u
    WHERE u.count = {num_ingredients};
    """
    ids = cur.execute(query).fetchall()
    return [id[0] for id in ids]


def recipes_meal_ingredients(cur, meal, *ingredients):
    ids_in_meal = get_id_recipes_for_meal(meal, cur)
    ids_in_ingredients = get_id_recipes_with_all_ingredients(cur, *ingredients)
    ids = set(ids_in_meal).intersection(set(ids_in_ingredients))
    if len(ids) == 0:
        return []
    ids = [str(i) for i in ids]
    formatted = '(' + ', '.join(ids) + ')'
    query = f'SELECT recipe_name FROM recipes WHERE recipe_id IN {formatted}'
    names = cur.execute(query).fetchall()
    return [name[0] for name in names]


def main(cur, meals, ingredients):
    names = []
    for meal in meals:
        names += recipes_meal_ingredients(cur, meal, *ingredients)
    return list(set(names))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Food blog")
    parser.add_argument("db")
    parser.add_argument("--ingredients")
    parser.add_argument("--meals")
    args = parser.parse_args()
    db_name, ingredients, meals = args.db, args.ingredients, args.meals
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    if ingredients is None and meals is None:
        for table in tables:
            cursor.execute(tables[table])
            if table not in ('meals', 'measures', 'ingredients'):
                continue
            entries = [(item,) for item in data[table]]
            cursor.executemany(f'INSERT INTO {table} VALUES (null, ?)', entries)
        conn.commit()
        fill_recipies(cursor, conn)
    else:
        meals = meals.split(',')
        ingredients = ingredients.split(',')
        names = main(cursor, meals=meals, ingredients=ingredients)
        if names:
            print(f'Recipes selected for you: {", ".join(names)}')
        else:
            print('There are no such recipes in the database.')
    conn.close()
