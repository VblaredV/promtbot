from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from utils.texts import get_text
from utils.keyboards import back_button
from handlers.library import PROMPTS_DATA, NEURAL_NETS, STYLES

SEARCH_STATE = 1

async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    buttons = [[InlineKeyboardButton(name, callback_data=f"search|style|{name}")] for name in NEURAL_NETS]
    buttons.append([back_button(lang, "menu|main")])
    await query.edit_message_text("🔍 Выбери нейросеть для поиска:", reply_markup=InlineKeyboardMarkup(buttons))
    return SEARCH_STATE

async def search_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    net = query.data.split("|")[-1]
    context.user_data["search_net"] = net
    buttons = [[InlineKeyboardButton(style, callback_data=f"search|category|{net}|{style}")] for style in STYLES]
    buttons.append([back_button(lang, "menu|search")])
    await query.edit_message_text(f"{net} — выбери стиль:", reply_markup=InlineKeyboardMarkup(buttons))
    return SEARCH_STATE

async def search_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    parts = query.data.split("|")
    net, style = parts[2], parts[3]
    context.user_data["search_net"] = net
    context.user_data["search_style"] = style

    categories = list(PROMPTS_DATA[net][style].keys())
    context.user_data["search_categories"] = categories   # сохраняем список

    buttons = []
    for idx, cat in enumerate(categories):
        buttons.append([InlineKeyboardButton(cat, callback_data=f"search|setcat|{idx}")])  # только индекс

    buttons.append([back_button(lang, f"search|style|{net}")])
    await query.edit_message_text(f"{net} > {style} — выбери категорию:", reply_markup=InlineKeyboardMarkup(buttons))
    return SEARCH_STATE

async def search_set_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    idx = int(query.data.split("|")[-1])
    categories = context.user_data.get("search_categories", [])
    if idx >= len(categories):
        await query.answer("Ошибка категории", show_alert=True)
        return SEARCH_STATE
    category = categories[idx]
    context.user_data["search_category"] = category
    await query.edit_message_text("✏️ Введи ключевые слова для поиска:")
    return SEARCH_STATE

async def search_do(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    keyword = update.message.text.lower()
    net = context.user_data.get("search_net")
    style = context.user_data.get("search_style")
    category = context.user_data.get("search_category")

    prompts = PROMPTS_DATA.get(net, {}).get(style, {}).get(category, [])
    results = [p for p in prompts if keyword in p["title"].lower() or keyword in p["text"].lower()]

    if not results:
        await update.message.reply_text(
            "🔍 Ничего не найдено.",
            reply_markup=InlineKeyboardMarkup([[back_button(lang, "menu|search")]])
        )
        return ConversationHandler.END

    text = "\n\n".join([f"*{p['title']}*\n{p['text'][:200]}..." for p in results[:6]])
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[back_button(lang, "menu|search")]])
    )
    return ConversationHandler.END

search_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(search_start, pattern="^menu\\|search$")],
    states={
        SEARCH_STATE: [
            CallbackQueryHandler(search_style, pattern="^search\\|style\\|"),
            CallbackQueryHandler(search_category, pattern="^search\\|category\\|"),
            CallbackQueryHandler(search_set_category, pattern="^search\\|setcat\\|"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, search_do),
        ]
    },
    fallbacks=[],
)