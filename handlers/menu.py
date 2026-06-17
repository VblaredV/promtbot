from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import main_menu_keyboard
from utils.texts import get_text
from config import ADMIN_IDS

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Универсальный показ главного меню.
    Если пришёл callback_query – редактирует сообщение,
    иначе отправляет новое.
    """
    lang = context.user_data.get("lang", "ru")
    user_id = update.effective_user.id
    is_admin = user_id in ADMIN_IDS
    keyboard = main_menu_keyboard(lang, is_admin)
    text = get_text(lang, "welcome_menu")

    if update.callback_query:
        # Это колбэк от кнопки
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=keyboard)
    else:
        # Обычное сообщение – отправляем новое
        await update.message.reply_text(text, reply_markup=keyboard)