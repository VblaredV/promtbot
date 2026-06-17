from datetime import datetime, timedelta
import aiosqlite
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.texts import get_text
from utils.db import get_user, update_user_balance, DB_PATH
from utils.keyboards import back_button

async def shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню магазина."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    user = await get_user(query.from_user.id)
    balance = user[6] if user else 0
    text = f"💰 Баланс: {balance} монет\n\n{get_text(lang, 'payment_instructions')}"
    buttons = [
        [InlineKeyboardButton(get_text(lang, "shop_coins"), callback_data="shop|buycoins")],
        [InlineKeyboardButton(get_text(lang, "shop_subscription"), callback_data="shop|sub")],
        [back_button(lang, "menu|main")]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def buy_coins_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор пакета монет."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    buttons = [
        [InlineKeyboardButton("🪙 69 монет (25 ⭐)", callback_data="shop|pay|69")],
        [InlineKeyboardButton("🪙 138 монет (50 ⭐)", callback_data="shop|pay|138")],
        [InlineKeyboardButton("🪙 207 монет (75 ⭐)", callback_data="shop|pay|207")],
        [back_button(lang, "menu|shop")]
    ]
    await query.edit_message_text("Выбери пакет монет:", reply_markup=InlineKeyboardMarkup(buttons))

async def payment_instructions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает инструкцию для оплаты выбранного пакета."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    amount = int(query.data.split("|")[-1])
    stars = amount // 69 * 25
    text = (
        f"💳 Для покупки {amount} монет отправь {stars} звёзд на канал {CHANNEL_ID} или используй другой метод.\n"
        "После оплаты нажми «Я оплатил»."
    )
    buttons = [
        [InlineKeyboardButton(get_text(lang, "payment_done"), callback_data=f"shop|paid|{amount}")],
        [back_button(lang, "menu|shop")]
    ]
    # Нужен CHANNEL_ID из конфига – импортируем
    from config import CHANNEL_ID
    text = text.replace("{CHANNEL_ID}", CHANNEL_ID) if "{CHANNEL_ID}" in text else text
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def payment_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатия «Я оплатил» — зачисляет монеты (заглушка, без реальной проверки)."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    amount = int(query.data.split("|")[-1])
    user_id = query.from_user.id
    await update_user_balance(user_id, amount)
    await query.edit_message_text(
        f"✅ Баланс пополнен на {amount} монет!",
        reply_markup=InlineKeyboardMarkup([[back_button(lang, "menu|shop")]])
    )

async def buy_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Покупка подписки за 552 монеты."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    user_id = query.from_user.id
    user = await get_user(user_id)
    balance = user[6] if user else 0

    if balance < 552:
        await query.answer("😔 Недостаточно монет. Нужно 552.", show_alert=True)
        return

    await update_user_balance(user_id, -552)
    new_sub = (datetime.now() + timedelta(days=30)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET subscription_until=? WHERE user_id=?", (new_sub, user_id))
        await db.commit()
    await query.edit_message_text(
        "🎉 Подписка активирована на 30 дней!",
        reply_markup=InlineKeyboardMarkup([[back_button(lang, "menu|shop")]])
    )