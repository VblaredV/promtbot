import json
import aiosqlite
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from utils.texts import get_text
from utils.db import DB_PATH, get_user, ban_user, unban_user, update_user_balance
from utils.keyboards import back_button
from config import ADMIN_IDS, ITEMS_PER_PAGE

(
    ADMIN_MAIN, SEARCH_ID, BAN_ID, MSG_ID, MSG_TEXT,
    BALANCE_ID, BALANCE_AMOUNT, PREMIUM_ID,
    ADD_PROMPT_NET, ADD_PROMPT_STYLE, ADD_PROMPT_CATEGORY,
    ADD_PROMPT_TEXT, ADD_PROMPT_PRICE, ADD_PROMPT_PREMIUM,
    MSG_IMPORTANCE,
) = range(15)

try:
    with open("data/prompts.json", "r", encoding="utf-8-sig") as f:
        PROMPTS_DATA = json.load(f)
except Exception:
    PROMPTS_DATA = {}

NEURAL_NETS = list(PROMPTS_DATA.keys()) if PROMPTS_DATA else ["DeepSeek", "Gemini", "ChatGPT", "Claude"]
STYLES = ["Ryzen", "Adecuad", "Gnomo"]
LANG = "ru"   # админка на русском? для мультиязычности можно брать язык из context.user_data, но т.к. админов двое, оставим русский

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id not in ADMIN_IDS:
        await query.answer(get_text("ru", "error"), show_alert=True)
        return
    buttons = [
        [InlineKeyboardButton("🔍 Поиск пользователя", callback_data="admin|search")],
        [InlineKeyboardButton("🚫 Бан/разбан", callback_data="admin|ban")],
        [InlineKeyboardButton("✉️ Написать сообщение", callback_data="admin|msg")],
        [InlineKeyboardButton("💰 Изменить баланс", callback_data="admin|balance")],
        [InlineKeyboardButton("⭐ Выдать премиум", callback_data="admin|premium")],
        [InlineKeyboardButton("📥 Добавить промт", callback_data="admin|addprompt")],
        [back_button(LANG, "menu|main")]
    ]
    await query.edit_message_text(get_text(LANG, "admin_menu_title"), reply_markup=InlineKeyboardMarkup(buttons))
    return ADMIN_MAIN

# --- Поиск пользователя ---
async def admin_search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(get_text(LANG, "admin_search_prompt"))
    return SEARCH_ID

async def admin_search_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE unique_id=?", (uid,))
        user = await cursor.fetchone()
    if user:
        info = (
            f"TG ID: {user[0]}\n"
            f"Username: @{user[1]}\n"
            f"Unique ID: {user[2]}\n"
            f"Язык: {user[3]}\n"
            f"Premium: {'Да' if user[4] else 'Нет'}\n"
            f"Banned: {'Да' if user[5] else 'Нет'}\n"
            f"Баланс: {user[6]} монет\n"
            f"Подписка до: {user[7] or 'нет'}"
        )
    else:
        info = get_text(LANG, "admin_user_not_found")
    await update.message.reply_text(info, reply_markup=InlineKeyboardMarkup([[back_button(LANG, "menu|admin")]]))
    return ConversationHandler.END

# --- Бан/разбан ---
async def admin_ban_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(get_text(LANG, "admin_ban_prompt"))
    return BAN_ID

async def admin_ban_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id, banned FROM users WHERE unique_id=?", (uid,))
        user = await cursor.fetchone()
        if not user:
            await update.message.reply_text(get_text(LANG, "admin_user_not_found"))
            return ConversationHandler.END
        if user[1]:
            await unban_user(user[0])
            text = get_text(LANG, "admin_unban_success")
        else:
            await ban_user(user[0])
            text = get_text(LANG, "admin_ban_success")
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup([[back_button(LANG, "menu|admin")]]))
    return ConversationHandler.END

# --- Отправка сообщения (с выбором важности) ---
async def admin_msg_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(get_text(LANG, "admin_msg_prompt"))
    return MSG_ID

async def admin_msg_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    context.user_data["admin_msg_uid"] = uid
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text(LANG, "important_msg"), callback_data="msg_importance|1")],
        [InlineKeyboardButton(get_text(LANG, "normal_msg"), callback_data="msg_importance|0")],
    ])
    await update.message.reply_text(get_text(LANG, "choose_importance"), reply_markup=keyboard)
    return MSG_IMPORTANCE

async def admin_msg_importance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    important = query.data.split("|")[1] == "1"
    context.user_data["admin_msg_important"] = important
    await query.edit_message_text(get_text(LANG, "admin_msg_text_prompt"))
    return MSG_TEXT

async def admin_msg_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = context.user_data.get("admin_msg_uid")
    text = update.message.text
    important = context.user_data.get("admin_msg_important", False)

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id, notifications_enabled FROM users WHERE unique_id=?", (uid,))
        user = await cursor.fetchone()
        if not user:
            await update.message.reply_text(get_text(LANG, "admin_user_not_found"))
            return ConversationHandler.END

        target_id = user[0]
        notifications_on = user[1] == 1 if len(user) > 1 else True

        # Если сообщение не важное и уведомления выключены – отказ
        if not important and not notifications_on:
            await update.message.reply_text(
                get_text(LANG, "notification_disabled_normal"),
                reply_markup=InlineKeyboardMarkup([[back_button(LANG, "menu|admin")]])
            )
            return ConversationHandler.END

        # Формируем префикс
        prefix = get_text(LANG, "admin_msg_important_prefix") if important else get_text(LANG, "admin_msg_normal_prefix")
        full_msg = f"{prefix} {get_text(LANG, 'admin_msg_from')}:\n{text}"

        try:
            await context.bot.send_message(target_id, full_msg)
            await update.message.reply_text(
                get_text(LANG, "admin_msg_sent"),
                reply_markup=InlineKeyboardMarkup([[back_button(LANG, "menu|admin")]])
            )
        except Exception as e:
            await update.message.reply_text(
                get_text(LANG, "admin_msg_send_error", error=str(e)),
                reply_markup=InlineKeyboardMarkup([[back_button(LANG, "menu|admin")]])
            )
    return ConversationHandler.END

# --- Изменить баланс ---
async def admin_balance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(get_text(LANG, "admin_balance_prompt"))
    return BALANCE_ID

async def admin_balance_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["admin_bal_uid"] = update.message.text.strip()
    await update.message.reply_text(get_text(LANG, "admin_balance_amount_prompt"))
    return BALANCE_AMOUNT

async def admin_balance_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = context.user_data.get("admin_bal_uid")
    try:
        amount = int(update.message.text)
    except ValueError:
        await update.message.reply_text(get_text(LANG, "admin_enter_number"))
        return ConversationHandler.END
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users WHERE unique_id=?", (uid,))
        user = await cursor.fetchone()
        if not user:
            await update.message.reply_text(get_text(LANG, "admin_user_not_found"))
            return ConversationHandler.END
        await update_user_balance(user[0], amount)
        updated_user = await get_user(user[0])
        balance = updated_user[6] if updated_user else "?"
        text = get_text(LANG, "admin_balance_result", balance)
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup([[back_button(LANG, "menu|admin")]]))
    return ConversationHandler.END

# --- Выдать премиум ---
async def admin_premium_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(get_text(LANG, "admin_premium_prompt"))
    return PREMIUM_ID

async def admin_premium_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users WHERE unique_id=?", (uid,))
        user = await cursor.fetchone()
        if not user:
            await update.message.reply_text(get_text(LANG, "admin_user_not_found"))
            return ConversationHandler.END
        await db.execute("UPDATE users SET premium=1 WHERE user_id=?", (user[0],))
        await db.commit()
    await update.message.reply_text(get_text(LANG, "admin_premium_result"),
                                    reply_markup=InlineKeyboardMarkup([[back_button(LANG, "menu|admin")]]))
    return ConversationHandler.END

# --- Добавить промт ---
async def admin_addprompt_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    buttons = [[InlineKeyboardButton(name, callback_data=f"addprompt|net|{name}")] for name in NEURAL_NETS]
    buttons.append([back_button(LANG, "menu|admin")])
    await query.edit_message_text(get_text(LANG, "admin_addprompt_net"), reply_markup=InlineKeyboardMarkup(buttons))
    return ADD_PROMPT_NET

async def admin_addprompt_net(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    net = query.data.split("|")[-1]
    context.user_data["addprompt_net"] = net
    buttons = [[InlineKeyboardButton(style, callback_data=f"addprompt|style|{style}")] for style in STYLES]
    buttons.append([back_button(LANG, "admin|addprompt")])
    await query.edit_message_text(get_text(LANG, "admin_addprompt_style", net), reply_markup=InlineKeyboardMarkup(buttons))
    return ADD_PROMPT_STYLE

async def admin_addprompt_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    style = query.data.split("|")[-1]
    context.user_data["addprompt_style"] = style
    await query.edit_message_text(get_text(LANG, "admin_addprompt_cat"))
    return ADD_PROMPT_CATEGORY

async def admin_addprompt_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat = update.message.text.strip()
    context.user_data["addprompt_category"] = cat
    await update.message.reply_text(get_text(LANG, "admin_addprompt_text"))
    return ADD_PROMPT_TEXT

async def admin_addprompt_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        file = await update.message.document.get_file()
        content = (await file.download_as_bytearray()).decode("utf-8")
    else:
        content = update.message.text
    lines = content.strip().split("\n", 1)
    title = lines[0].strip()
    body = lines[1].strip() if len(lines) > 1 else ""
    context.user_data["addprompt_title"] = title
    context.user_data["addprompt_body"] = body
    await update.message.reply_text(get_text(LANG, "admin_addprompt_price"))
    return ADD_PROMPT_PRICE

async def admin_addprompt_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = int(update.message.text)
    except ValueError:
        await update.message.reply_text(get_text(LANG, "admin_enter_number"))
        return ADD_PROMPT_PRICE
    context.user_data["addprompt_price"] = price
    await update.message.reply_text(get_text(LANG, "admin_addprompt_premium"))
    return ADD_PROMPT_PREMIUM

async def admin_addprompt_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    premium_only = update.message.text.strip() == "1"
    net = context.user_data["addprompt_net"]
    style = context.user_data["addprompt_style"]
    category = context.user_data["addprompt_category"]
    title = context.user_data["addprompt_title"]
    body = context.user_data["addprompt_body"]
    price = context.user_data["addprompt_price"]

    if net not in PROMPTS_DATA:
        PROMPTS_DATA[net] = {}
    if style not in PROMPTS_DATA[net]:
        PROMPTS_DATA[net][style] = {}
    if category not in PROMPTS_DATA[net][style]:
        PROMPTS_DATA[net][style][category] = []
    PROMPTS_DATA[net][style][category].append({
        "title": title,
        "text": body,
        "price": price,
        "premium_only": premium_only
    })

    with open("data/prompts.json", "w", encoding="utf-8-sig") as f:
        json.dump(PROMPTS_DATA, f, ensure_ascii=False, indent=2)

    await update.message.reply_text(get_text(LANG, "admin_prompt_saved"),
                                    reply_markup=InlineKeyboardMarkup([[back_button(LANG, "menu|admin")]]))
    return ConversationHandler.END

# --- ConversationHandler'ы ---
admin_search_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(admin_search_start, pattern="^admin\\|search$")],
    states={SEARCH_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_search_result)]},
    fallbacks=[],
)
admin_ban_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(admin_ban_start, pattern="^admin\\|ban$")],
    states={BAN_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_ban_execute)]},
    fallbacks=[],
)
admin_msg_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(admin_msg_start, pattern="^admin\\|msg$")],
    states={
        MSG_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_msg_get_id)],
        MSG_IMPORTANCE: [CallbackQueryHandler(admin_msg_importance, pattern="^msg_importance\\|")],
        MSG_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_msg_send)],
    },
    fallbacks=[],
)
admin_balance_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(admin_balance_start, pattern="^admin\\|balance$")],
    states={
        BALANCE_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_balance_get_id)],
        BALANCE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_balance_execute)],
    },
    fallbacks=[],
)
admin_premium_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(admin_premium_start, pattern="^admin\\|premium$")],
    states={PREMIUM_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_premium_execute)]},
    fallbacks=[],
)
admin_addprompt_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(admin_addprompt_start, pattern="^admin\\|addprompt$")],
    states={
        ADD_PROMPT_NET: [CallbackQueryHandler(admin_addprompt_net, pattern="^addprompt\\|net\\|")],
        ADD_PROMPT_STYLE: [CallbackQueryHandler(admin_addprompt_style, pattern="^addprompt\\|style\\|")],
        ADD_PROMPT_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_addprompt_category)],
        ADD_PROMPT_TEXT: [MessageHandler(filters.TEXT | filters.Document.ALL, admin_addprompt_text)],
        ADD_PROMPT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_addprompt_price)],
        ADD_PROMPT_PREMIUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_addprompt_save)],
    },
    fallbacks=[],
)