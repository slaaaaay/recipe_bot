import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("bot_token")
api_key = os.getenv("api_key")
url = "https://api.spoonacular.com"
