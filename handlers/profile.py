import aiosqlite
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.texts import get_text
from utils.db import get_user, get_favorites, get_referral_stats, DB_PATH
from utils.keyboards import back_button, language_selection_keyboard

async def profile_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    user_id = query.from_user.id
    user = await get_user(user_id)

    if not user:
        await query.edit_message_text(
            get_text(lang, "profile_not_found"),
            reply_markup=InlineKeyboardMarkup([[back_button(lang, "menu|main")]])
        )
        return

    unique_id = user[2]
    username = user[1] if user[1] else get_text(lang, "username_none")
    language = get_text(lang, "language_rus") if user[3] == "ru" else get_text(lang, "language_eng")
    sub_until = user[7] if user[7] else get_text(lang, "subscription_none")
    balance = user[6] if len(user) > 6 else 0
    notifications = get_text(lang, "notifications_on") if len(user) > 8 and user[8] else get_text(lang, "notifications_off")

    text = get_text(
        lang, "profile_info",
        unique_id=unique_id,
        username=username,
        language=language,
        subscription_until=sub_until,
        balance=balance,
        notifications=notifications
    )

    # Кнопка уведомлений динамическая
    notif_btn_text = get_text(lang, "notifications_on_btn") if (len(user) > 8 and user[8]) else get_text(lang, "notifications_off_btn")

    buttons = [
        [InlineKeyboardButton("⭐ Избранное", callback_data="profile|fav")],
        [InlineKeyboardButton("🤝 Реферальная система", callback_data="profile|referral")],
        [InlineKeyboardButton(notif_btn_text, callback_data="profile|togglenotif")],
        [InlineKeyboardButton("🌐 Сменить язык", callback_data="profile|changelang")],
        [back_button(lang, "menu|main")]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def show_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    user_id = query.from_user.id
    fav_ids = await get_favorites(user_id)

    if not fav_ids:
        await query.edit_message_text(
            get_text(lang, "favorites_empty"),
            reply_markup=InlineKeyboardMarkup([[back_button(lang, "menu|profile")]])
        )
        return

    text = get_text(lang, "fav_title") + "\n" + "\n".join(f"• {pid}" for pid in fav_ids[:20])
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([[back_button(lang, "menu|profile")]])
    )

async def referral_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    user_id = query.from_user.id
    user = await get_user(user_id)
    if not user:
        return

    unique_id = user[2]
    ref_link = f"https://t.me/promtlibary_bot?start=invite_{unique_id}"
    invited, active, subscribed, earned, available, withdrawn = await get_referral_stats(user_id)

    text = get_text(
        lang, "referral_text",
        ref_link=ref_link,
        invited=invited,
        active=active,
        subscribed=subscribed,
        earned=earned,
        available=available,
        withdrawn=withdrawn
    )

    buttons = [
        [InlineKeyboardButton(get_text(lang, "withdraw_request"), callback_data="profile|withdraw")],
        [back_button(lang, "menu|profile")]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        get_text("ru", "choose_lang"),
        reply_markup=language_selection_keyboard()
    )

async def toggle_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    user_id = query.from_user.id
    user = await get_user(user_id)
    if not user:
        return

    new_val = 0 if (len(user) > 8 and user[8]) else 1
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET notifications_enabled=? WHERE user_id=?", (new_val, user_id))
        await db.commit()

    status = get_text(lang, "notifications_on") if new_val else get_text(lang, "notifications_off")
    await query.answer(f"Уведомления {status}", show_alert=True)