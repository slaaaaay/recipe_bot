from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command
from states.states import RecipeSearch, RandomRecipe, FavoriteRecipes
from logs.logger import logger


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    logger.info(f"User {message.from_user.id} started the bot")
    await message.answer("Привет! Это бот для поиска рецептов\n Используй /help для списка доступных команд")

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Получить справку\n"
        "/search - Поиск рецептов\n"
        "/random - Случайные рецепты\n"
        "/favorites - Мои сохраненные рецепты"
    )
    await message.answer(help_text)

@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    await message.answer("Введите название блюда для поиска: ")
    await state.set_state(RecipeSearch.waiting_for_query)
    logger.info(f"User {message.from_user.id} requested search")

@router.message(Command("random"))
async def cmd_random(message: Message, state: FSMContext):
    await message.answer("Сколько рецептов вы хотите получить?")
    await state.set_state(RandomRecipe.showing_recipe)
    logger.info(f"User {message.from_user.id} requested random recipes")

@router.message(Command("favorites"))
async def cmd_favorites(message: Message, state: FSMContext):

    await message.answer("Сколько рецептов из избранного вы хотите получить за раз?")
    await state.set_state(FavoriteRecipes.viewing_recipe)
    logger.info(f"User {message.from_user.id} requested favorites")