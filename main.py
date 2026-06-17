import asyncio
import sys
import logging
import re
import traceback
import warnings
import nest_asyncio
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from telegram import Update
from telegram.ext import ContextTypes

# ---------- Фикс для Windows ----------
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
nest_asyncio.apply()
warnings.filterwarnings("ignore", category=UserWarning)

# ---------- config ----------
from config import BOT_TOKEN

# ---------- db ----------
from utils.db import init_db, get_user

# ---------- handlers ----------
from handlers.start import start, check_subs, choose_lang
from handlers.menu import show_main_menu
from handlers.library import (
    neural_net_selection,
    style_selection,
    category_selection,
    prompts_selection,
    prompt_detail,
    buy_prompt,
    toggle_favorite,
)
from handlers.search import search_conv_handler
from handlers.profile import (
    profile_menu,
    show_favorites,
    referral_system,
    change_language,
    toggle_notifications,
)
from handlers.shop import (
    shop_menu,
    buy_coins_menu,
    payment_instructions,
    payment_done,
    buy_subscription,
)
from handlers.admin import (
    admin_menu,
    admin_search_conv,
    admin_ban_conv,
    admin_msg_conv,
    admin_balance_conv,
    admin_premium_conv,
    admin_addprompt_conv,
)

# ---------- logging ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("BotLogger")

# ---------- ФИЛЬТР ДЛЯ СКРЫТИЯ ТОКЕНА ----------
class TokenFilter(logging.Filter):
    def filter(self, record):
        record.msg = re.sub(r'\d+:[A-Za-z0-9_-]+', '***TOKEN***', str(record.msg))
        if record.args:
            record.args = tuple(
                re.sub(r'\d+:[A-Za-z0-9_-]+', '***TOKEN***', str(a)) for a in record.args
            )
        return True

logging.getLogger().addFilter(TokenFilter())
logging.getLogger("httpx").setLevel(logging.WARNING)

# ---------- MIDDLEWARE для логирования каждого обновления ----------
async def log_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user = update.effective_user
        text = update.message.text or update.message.caption or ''
        if text.startswith('/'):
            logger.info(f"Update: command from {user.id}: '{text}'")
        else:
            logger.info(f"Update: message from {user.id}: '{text[:100]}'")
    elif update.callback_query:
        user = update.callback_query.from_user
        data = update.callback_query.data
        logger.info(f"Update: callback_query from {user.id}: data='{data}'")
    else:
        logger.info(f"Update: {update}")
    return None

# ---------- ОБРАБОТЧИК ОШИБОК ----------
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    file_line = "Неизвестно"
    for line in tb_list:
        if 'File "' in line:
            parts = line.strip().split(", ")
            if len(parts) >= 2:
                file_line = f"{parts[0]}, {parts[1]}"
                break
    logger.error(
        f"Ошибка при обработке обновления: {context.error}\n"
        f"Место: {file_line}\n"
        f"Полный трейсбек:\n{tb_string}"
    )

# ---------- ГЛАВНАЯ АСИНХРОННАЯ ФУНКЦИЯ ----------
async def main():
    await init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Middleware логирования
    app.add_handler(MessageHandler(filters.ALL, log_update), group=-1)

    # /start и проверка подписки
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_subs, pattern="^check_subs$"))
    app.add_handler(CallbackQueryHandler(choose_lang, pattern="^lang\\|"))
    app.add_handler(CallbackQueryHandler(show_main_menu, pattern="^menu\\|main$"))

    # Библиотека
    app.add_handler(CallbackQueryHandler(neural_net_selection, pattern="^menu\\|library$"))
    app.add_handler(CallbackQueryHandler(style_selection, pattern="^lib\\|style\\|"))
    app.add_handler(CallbackQueryHandler(category_selection, pattern="^lib\\|category\\|"))
    app.add_handler(CallbackQueryHandler(prompts_selection, pattern="^lib\\|prompts\\|"))
    app.add_handler(CallbackQueryHandler(prompt_detail, pattern="^lib\\|detail\\|"))
    app.add_handler(CallbackQueryHandler(buy_prompt, pattern="^lib\\|buy\\|"))
    app.add_handler(CallbackQueryHandler(toggle_favorite, pattern="^fav\\|"))

    # Поиск
    app.add_handler(search_conv_handler)

    # Профиль
    app.add_handler(CallbackQueryHandler(profile_menu, pattern="^menu\\|profile$"))
    app.add_handler(CallbackQueryHandler(show_favorites, pattern="^profile\\|fav$"))
    app.add_handler(CallbackQueryHandler(referral_system, pattern="^profile\\|referral$"))
    app.add_handler(CallbackQueryHandler(change_language, pattern="^profile\\|changelang$"))
    app.add_handler(CallbackQueryHandler(toggle_notifications, pattern="^profile\\|togglenotif$"))

    # Магазин
    app.add_handler(CallbackQueryHandler(shop_menu, pattern="^menu\\|shop$"))
    app.add_handler(CallbackQueryHandler(buy_coins_menu, pattern="^shop\\|buycoins$"))
    app.add_handler(CallbackQueryHandler(payment_instructions, pattern="^shop\\|pay\\|"))
    app.add_handler(CallbackQueryHandler(payment_done, pattern="^shop\\|paid\\|"))
    app.add_handler(CallbackQueryHandler(buy_subscription, pattern="^shop\\|sub$"))

    # Админка
    app.add_handler(CallbackQueryHandler(admin_menu, pattern="^menu\\|admin$"))
    app.add_handler(admin_search_conv)
    app.add_handler(admin_ban_conv)
    app.add_handler(admin_msg_conv)
    app.add_handler(admin_balance_conv)
    app.add_handler(admin_premium_conv)
    app.add_handler(admin_addprompt_conv)

    # Обработчик ошибок
    app.add_error_handler(error_handler)

    # Любое текстовое сообщение (не команда) → главное меню
    async def show_menu_on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        db_user = await get_user(user_id)
        if db_user and db_user[3] and db_user[3] != '':
            await show_main_menu(update, context)
        else:
            await start(update, context)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, show_menu_on_message))

    logger.info("Бот запущен. Ожидаю команды...")
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")