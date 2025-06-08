import json
import os
from typing import Dict, List
from pathlib import Path
from logs.logger import logger


class JSONStorage:
    def __init__(self, file_path: str = "storage/user_data.json"):
        self.file_path = file_path
        Path(os.path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump({"favorites": {}}, f)

    def _read_data(self):
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"favorites": {}}

    def _write_data(self, data: Dict):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    def add_favorite(self, user_id: int, recipe_id: int, recipe_data: Dict):
        data = self._read_data()
        if str(user_id) not in data["favorites"]:
            data["favorites"][str(user_id)] = {}
        data["favorites"][str(user_id)][str(recipe_id)] = recipe_data
        self._write_data(data)
        logger.info(f"Added favorite recipe {recipe_id} for user {user_id}")

    def remove_favorite(self, user_id: int, recipe_id: int):
        data = self._read_data()
        if str(user_id) in data["favorites"] and str(recipe_id) in data["favorites"][str(user_id)]:
            del data["favorites"][str(user_id)][str(recipe_id)]
            self._write_data(data)
            logger.info(f"Removed favorite recipe {recipe_id} for user {user_id}")
            return True
        return False

    def get_favorites(self, user_id: int) -> List[Dict]:
        data = self._read_data()
        if str(user_id) in data["favorites"]:
            return list(data["favorites"][str(user_id)].values())
        return []

    def is_favorite(self, user_id: int, recipe_id: int) -> bool:
        data = self._read_data()
        return (str(user_id) in data["favorites"] and
                str(recipe_id) in data["favorites"][str(user_id)])


