import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8902146615:AAFoTo-hfvZO2gwOgL9HGqtIR4NOohuZ0k0")
CHANNEL_ID = "@PromtTotem"          # username канала для проверки подписки
PROMOT_CHANNEL = "https://t.me/PromtTotem"  # ссылка на канал (если понадобится)
ADMIN_IDS = {6136743814, 8776998479}
ITEMS_PER_PAGE = 6                  # сколько элементов на одной странице