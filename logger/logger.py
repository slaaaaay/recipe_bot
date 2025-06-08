import logging
from pathlib import Path
from datetime import datetime


def setup_logger():
    """Настройка логгера с записью в файл и выводом в консоль"""
    log_dir = "logs"
    Path(log_dir).mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            # дата, чтобы на кажддый день был отдельный файл с историей, мне показалоь это удобно
            logging.FileHandler(f"logs/bot_{datetime.now().strftime('%d%m%Y')}.log"),
            logging.StreamHandler()
        ]
    )

    # Настройка логгера для aiohttp
    aiohttp_logger = logging.getLogger('aiohttp')
    aiohttp_logger.setLevel(logging.WARNING)


# глобальный объект логгера
logger = logging.getLogger(__name__)

