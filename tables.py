define_meals = '''
CREATE TABLE IF NOT EXISTS meals (
    meal_id INTEGER PRIMARY KEY,
    meal_name TEXT UNIQUE NOT NULL
    );
'''

define_measures = '''
CREATE TABLE IF NOT EXISTS measures (
    measure_id INTEGER PRIMARY KEY,
    measure_name TEXT UNIQUE
    );
'''

define_ingredients = '''
CREATE TABLE IF NOT EXISTS ingredients (
    ingredient_id INTEGER PRIMARY KEY,
    ingredient_name TEXT UNIQUE NOT NULL
    );
'''

define_recipes = '''
CREATE TABLE IF NOT EXISTS recipes (
    recipe_id INTEGER PRIMARY KEY,
    recipe_name TEXT NOT NULL,
    recipe_description TEXT
    );
'''

define_serve = '''
CREATE TABLE IF NOT EXISTS serve (
    serve_id INTEGER PRIMARY KEY,
    recipe_id INTEGER NOT NULL,
    meal_id INTEGER NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),
    FOREIGN KEY (meal_id) REFERENCES meals(meal_id)
    );
'''


define_quantity = '''
CREATE TABLE IF NOT EXISTS quantity (
    quantity_id INTEGER PRIMARY KEY, 
    measure_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL, 
    quantity INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    FOREIGN KEY (measure_id) REFERENCES measures(measure_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
    );
'''

tables = {
    'meals': define_meals,
    'measures': define_measures,
    'ingredients': define_ingredients,
    'recipes': define_recipes,
    'serve': define_serve,
    'quantity': define_quantity
}
