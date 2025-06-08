import aiohttp
import asyncio
from typing import Optional, Dict
from config.settings import api_key, url
from logs.logger import logger


class SpoonacularClient:
    def __init__(self):
        self.base_url = url
        self.api_key = api_key
        self.session = None
        self._upcoming_cache: Optional[Dict] = {}

    async def ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def search_recipes(self, query: str, number: int = 1):
        """Поиск рецептов по названию"""
        await self.ensure_session()
        params = {
            "query": query,
            "number": number
        }

        return await self._make_request("recipes/complexSearch", params)


    async def get_recipe_info(self, recipe_id: int):
        """Получение полной информации о рецепте"""
        await self.ensure_session()
        return await self._make_request(f"recipes/{recipe_id}/information", {})


    async def get_random_recipes(self, number: int = 5):
        """Получение случайных рецептов"""
        await self.ensure_session()
        return await self._make_request("recipes/random", {"number": number})

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None):
        '''запрос делает на сайтик'''
        if params is None:
            params = {}
        params["apiKey"] = self.api_key

        try:
            async with self.session.get(
                    f"{self.base_url}/{endpoint}",
                    params=params,
                    timeout=10
            ) as response:

                if response.status == 200:
                    data = await response.json()
                    return data

                logger.error(f"API error: {response.status}")
                return None
        except asyncio.TimeoutError:
            logger.error("API request timeout")
            return None
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None