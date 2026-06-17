from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.texts import get_text

def back_button(lang, callback_data="menu|main"):
    return InlineKeyboardButton(get_text(lang, "back"), callback_data=callback_data)

def main_menu_keyboard(lang, is_admin=False):
    """Главное меню с красивой раскладкой."""
    keyboard = [
        [InlineKeyboardButton(get_text(lang, "menu_profile"), callback_data="menu|profile")],
        [
            InlineKeyboardButton(get_text(lang, "menu_library"), callback_data="menu|library"),
            InlineKeyboardButton(get_text(lang, "menu_search"), callback_data="menu|search"),
        ],
        [InlineKeyboardButton(get_text(lang, "menu_shop"), callback_data="menu|shop")],
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton(get_text(lang, "menu_admin"), callback_data="menu|admin")])
    return InlineKeyboardMarkup(keyboard)

def language_selection_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang|ru"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang|en")]
    ])