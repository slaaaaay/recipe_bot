from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from datetime import datetime, timedelta
from logs.logger import logger


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self):
        self.user_timestamps = {}

    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        current_time = datetime.now()

        if user_id in self.user_timestamps:
            last_time = self.user_timestamps[user_id]
            if current_time - last_time < timedelta(seconds=1):
                logger.warning(f"User {user_id} throttled")
                if isinstance(event, types.Message):
                    await event.answer("Слишком много запросов. Пожалуйста, подождите.")
                return

        self.user_timestamps[user_id] = current_time
        return await handler(event, data)