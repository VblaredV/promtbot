import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.texts import get_text
from utils.subscription import is_subscribed
from utils.db import upsert_user, set_user_language, get_user
from utils.keyboards import language_selection_keyboard, main_menu_keyboard
from config import CHANNEL_ID, ADMIN_IDS

logger = logging.getLogger("BotLogger")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    logger.info(f"Запущен /start от пользователя {user.id} (@{user.username})")

    if args and args[0].startswith("invite_"):
        inviter_unique = args[0].split("_")[1]
        from utils.db import add_referral, update_user_balance
        import aiosqlite
        from utils.db import DB_PATH
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT user_id FROM users WHERE unique_id=?", (inviter_unique,))
            row = await cursor.fetchone()
            if row and row[0] != user.id:
                await add_referral(row[0], user.id)
                await update_user_balance(row[0], 69)
                await update_user_balance(user.id, 69)
                logger.info(f"Реферальная программа: {user.id} приглашён, бонусы начислены")

    await upsert_user(user.id, user.username)

    if not await is_subscribed(context.bot, user.id):
        await update.message.reply_text(
            get_text("ru", "start_welcome", channel=CHANNEL_ID),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text("ru", "check_subscribe"), callback_data="check_subs")
            ]])
        )
        logger.info(f"Пользователь {user.id} не подписан – предложена проверка")
        return

    db_user = await get_user(user.id)
    language = db_user[3] if db_user and db_user[3] else None

    if language and language != '':
        context.user_data["lang"] = language
        await show_main_menu_direct(update, context, user.id, language)
        logger.info(f"Пользователь {user.id} сразу перешёл в главное меню")
    else:
        await update.message.reply_text(
            get_text("ru", "choose_lang"),
            reply_markup=language_selection_keyboard()
        )
        logger.info(f"Пользователь {user.id} не выбрал язык – предложен выбор")

async def check_subs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    logger.info(f"Проверка подписки: пользователь {user.id}")
    if await is_subscribed(context.bot, user.id):
        db_user = await get_user(user.id)
        language = db_user[3] if db_user and db_user[3] else None
        if language and language != '':
            context.user_data["lang"] = language
            await show_main_menu_direct(update, context, user.id, language)
        else:
            await query.edit_message_text(
                get_text("ru", "choose_lang"),
                reply_markup=language_selection_keyboard()
            )
        logger.info(f"Подписка {user.id} подтверждена")
    else:
        await query.answer(get_text("ru", "not_subscribed"), show_alert=True)
        logger.info(f"Подписка {user.id} не подтверждена")

async def choose_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, lang = query.data.split("|")
    user_id = update.effective_user.id
    await set_user_language(user_id, lang)
    context.user_data["lang"] = lang
    logger.info(f"Пользователь {user_id} выбрал язык {lang}")
    await show_main_menu_direct(update, context, user_id, lang)

async def show_main_menu_direct(update, context, user_id, lang):
    is_admin = user_id in ADMIN_IDS
    if update.callback_query:
        await update.callback_query.edit_message_text(
            get_text(lang, "welcome_menu"),
            reply_markup=main_menu_keyboard(lang, is_admin)
        )
    else:
        await update.message.reply_text(
            get_text(lang, "welcome_menu"),
            reply_markup=main_menu_keyboard(lang, is_admin)
        )