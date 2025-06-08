from aiogram.fsm.state import State, StatesGroup

class RecipeSearch(StatesGroup):
    """Состояния для процесса поиска рецептов"""
    waiting_for_query = State()  # ждет ввода поискового запроса

class RandomRecipe(StatesGroup):
    """Состояния для работы со случайными рецептами"""
    showing_recipe = State()     # просмотр случайного рецепта

class FavoriteRecipes(StatesGroup):
    """Состояния для работы с избранными рецептами"""
    viewing = State()           # просмотр ленты избранных рецептов
    viewing_recipe = State()     # просмотр избранных рецептов


