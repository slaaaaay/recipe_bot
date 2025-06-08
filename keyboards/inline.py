from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def show_recipe_keyboard(recipe_id: int):
    buttons = [[InlineKeyboardButton(
            text="Показать рецепт",
            callback_data=f"view_recipe_{recipe_id}")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)




def recipe_keyboard(recipe_id: int, is_favorite: bool):
    buttons = []

    # Favorite button
    if is_favorite:
        fav_text = "Удалить из избранного"
        fav_action = "unfavorite"
    else:
        fav_text = "Добавить в избранное"
        fav_action = "favorite"

    buttons.append([InlineKeyboardButton(text=fav_text, callback_data=f"recipe_{fav_action}_{recipe_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def favorites_keyboard(recipe_id):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
                    text="Показать рецепт",
                    callback_data=f"view_recipe_{recipe_id}"), InlineKeyboardButton(
                    text="Удалить",
                    callback_data=f"recipe_unfavorite_{recipe_id}")]])

def favorites_more():
    return InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Да",
                                callback_data="show_more"
                            ),
                            InlineKeyboardButton(
                                text="Нет, выйти",
                                callback_data="cancel"
                            )
                        ]
                    ]
                )

