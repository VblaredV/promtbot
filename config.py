import sys

try:
    from private_config import BOT_TOKEN
except ImportError:
    print("Ошибка: создайте файл private_config.py с переменной BOT_TOKEN")
    sys.exit(1)

CHANNEL_ID = "@PromtTotem"
ADMIN_IDS = {6136743814, 8776998479}
ITEMS_PER_PAGE = 6