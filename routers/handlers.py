from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from services.api_client import SpoonacularClient
from storage.storage import JSONStorage
from keyboards.inline import recipe_keyboard, show_recipe_keyboard, favorites_more, favorites_keyboard
from states.states import RecipeSearch, RandomRecipe, FavoriteRecipes
from utils.formatters import format_recipe, format_recipe_instructions
from logs.logger import logger
from python_translator import Translator
translator = Translator()

router = Router()
api_client = SpoonacularClient()
storage = JSONStorage()


@router.message(StateFilter(RecipeSearch.waiting_for_query))
async def process_search_query(message: Message, state: FSMContext):
    query = message.text

    await message.answer(f"Ищу рецепты по запросу: {query}")
    query = translator.translate(query, 'english', 'russian')
    recipes = await api_client.search_recipes(str(query))
    if recipes['results'] != []:

        recipe = recipes['results'][0]

        recipe_id = recipe['id']
        recipe_photo = recipe['image']
        detailed_recipe = await api_client.get_recipe_info(recipe_id)
        if detailed_recipe:
            is_favorite = storage.is_favorite(message.from_user.id, recipe_id)
            keyboard = recipe_keyboard(recipe_id, is_favorite)

            await message.answer_photo(
                photo=recipe_photo,
                caption=format_recipe(detailed_recipe),
                reply_markup=keyboard
            )
            await message.answer(format_recipe_instructions(detailed_recipe))
        else:
            await message.answer("Не удалось загрузить информацию о рецепте")
    else:
        await message.answer("Ничего не найдено. Попробуйте другой запрос.")

    await state.clear()
    logger.info(f"User {message.from_user.id} searched for {query}")


@router.message(StateFilter(RandomRecipe.showing_recipe))
async def random_recipies(message: Message, state: FSMContext):
    count_of_recipies = message.text
    try:
        count_of_recipies = int(count_of_recipies)

    except ValueError("неверный формат ввода, необходимо ввести число"):
        await message.answer(str(ValueError))

    recipes = await api_client.get_random_recipes(count_of_recipies)
    print(recipes)

    if recipes['recipes'] != []:
         # каждый рецепт отдельным сообщением
        for recipe in recipes["recipes"]:
            caption = f"{recipe['title']}"
             # изображение с подписью
            await message.answer_photo(
                photo=recipe['image'],
                caption=caption,
                reply_markup=show_recipe_keyboard(recipe['id'])
            )
    else:
        await message.answer("Произошла ошибка, попробуйте еще раз")

    await state.set_state(state=None)
    logger.info(f"User {message.from_user.id} searched for {count_of_recipies} recipe/ies")


@router.callback_query(F.data.startswith("view_recipe_"))
async def recipe_details_random(callback: CallbackQuery, state: FSMContext):
    part, recipe_id = callback.data.split("_")[1:]
    recipe_id = int(recipe_id)
    detailed_recipe = await api_client.get_recipe_info(recipe_id)
    if detailed_recipe:
        is_favorite = storage.is_favorite(callback.from_user.id, recipe_id)
        keyboard = recipe_keyboard(recipe_id, is_favorite)

        await callback.message.answer_photo(photo=detailed_recipe.get('image', ''),
                                            caption=format_recipe(detailed_recipe), reply_markup=keyboard)
        await callback.message.answer(format_recipe_instructions(detailed_recipe))
    else:
        await callback.answer("Не удалось загрузить информацию о рецепте")
    logger.info(f"User {callback.from_user.id} searched for {recipe_id} details")

@router.message(StateFilter(FavoriteRecipes.viewing_recipe))
async def show_favorites(message: Message, state: FSMContext):
    batch_size = int(message.text)
    user_id = message.from_user.id
    favorites = storage.get_favorites(user_id)

    if not favorites:
        await message.answer("У вас пока нет избранных рецептов")
        return

    await state.update_data(
        favorites=favorites,
        index=0,
        batch_size=batch_size
    )
    await state.set_state(FavoriteRecipes.viewing)
    await show_next_batch(message, state)


async def show_next_batch(message: Message, state: FSMContext):
    data = await state.get_data()
    favorites = data["favorites"]
    index = data["index"]
    batch_size = data["batch_size"]

    end_index = min(index + batch_size, len(favorites))

    # отправляет часть рецептов
    for i in range(index, end_index):
        recipe = favorites[i]
        await message.answer_photo(
            photo=recipe['image'],
            caption=recipe['title'],
            reply_markup=favorites_keyboard(recipe['id'])
        )

    # индекс
    await state.update_data(index=end_index)

    # если остались рецепты - предлагает показать еще
    if end_index < len(favorites):
        await message.answer(
            "Показать еще избранные рецепты?",
            reply_markup=favorites_more()
        )
    else:
        await message.answer("Это все ваши избранные рецепты")
        await state.clear()


@router.callback_query(FavoriteRecipes.viewing, F.data == "show_more")
async def handle_show_more(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()  # удаляет кнопку "Показать еще"
    await show_next_batch(callback.message, state)


@router.callback_query(FavoriteRecipes.viewing, F.data == "cancel")
async def handle_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer("Просмотр завершен")
    await state.clear()


@router.callback_query(F.data.startswith("remove_"))
async def remove_favorite(callback: CallbackQuery, state: FSMContext):
    recipe_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    # удаляет из хранилища
    storage.remove_favorite(user_id, recipe_id)

    # обновление данных в состоянии
    data = await state.get_data()
    if "favorites" in data:
        data["favorites"] = [r for r in data["favorites"] if r["id"] != recipe_id]
        await state.update_data(favorites=data["favorites"])

    await callback.answer("Рецепт удален из избранного")
    await callback.message.delete()

@router.callback_query(F.data.startswith("recipe_"))
async def recipe_action(callback: CallbackQuery, state: FSMContext):
    action, recipe_id = callback.data.split("_")[1:]
    recipe_id = int(recipe_id)
    user_id = callback.from_user.id

    if action == "favorite":
        recipe_info = await api_client.get_recipe_info(recipe_id)
        if recipe_info:
            storage.add_favorite(user_id, recipe_id, {
                "id": recipe_id,
                "title": recipe_info["title"],
                "image": recipe_info["image"]
            })
            await callback.answer("Рецепт добавлен в избранное")
        else:
            await callback.answer("Не удалось добавить рецепт")
    elif action == "unfavorite":
        if storage.remove_favorite(user_id, recipe_id):
            await callback.answer("Рецепт удален из избранного")
        else:
            await callback.answer("Рецепт не найден в избранном")

    is_favorite = storage.is_favorite(user_id, recipe_id)

    await callback.message.edit_reply_markup(
        reply_markup=recipe_keyboard(recipe_id, is_favorite))
    logger.info(f"User {user_id} performed {action} on recipe {recipe_id}")

