import re
from python_translator import Translator
translator = Translator()
def format_recipe(recipe: dict):
    '''форматирует текст ингридиенты и выводит информацию, переведенную на русский'''

    ingredients = "\n".join(
        f"· {ingr['name'].capitalize()} - {ingr['amount']} {ingr['unit']}"
        for ingr in recipe.get("extendedIngredients", [])
    )
    ingredients_transl = translator.translate(ingredients, 'russian', 'english')

    return (
        f"{translator.translate(recipe['title'], 'russian', 'english')}\n\n"
        f"Время приготовления:{translator.translate(recipe['readyInMinutes'], 'russian', 'english')} мин\n"
        f"Порций: {translator.translate(recipe['servings'], 'russian', 'english')}\n\n"
        f"Ингредиенты:\n{ingredients_transl}\n\n"
    )

def clean_html(text):
    """чистит текст"""
    clean_text = re.sub(r'<[^>]+>', '\n', text)  # чистит все HTML-теги, заменяем на абзац
    clean_text = re.sub(r'\n\s*\n', '\n', clean_text)  # удаляет пустые строки
    return clean_text.strip()

def format_recipe_instructions(recipe: dict):
    """выводит инструкции к рецепту"""
    return f"Инструкции:\n{translator.translate(clean_html(recipe.get('instructions', 'Нет инструкций')), 'russian', 'english')}"
