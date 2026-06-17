import json
import math
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.texts import get_text
from utils.db import (
    get_user,
    has_purchased,
    add_purchased,
    update_user_balance,
    add_favorite,
    remove_favorite,
    get_favorites,
)
from utils.keyboards import back_button

with open("data/prompts.json", encoding="utf-8-sig") as f:
    PROMPTS_DATA = json.load(f)

NEURAL_NETS = list(PROMPTS_DATA.keys()) if PROMPTS_DATA else ["DeepSeek", "Gemini", "ChatGPT", "Claude"]
STYLES = ["Ryzen", "Adecuad", "Gnomo"]
ITEMS_PER_PAGE = 6

DEFAULT_CATEGORIES = [
    "Кодовый",
    "Развлекательный",
    "Для Учебы",
    "Для Рецептов На Кухне",
    "Для Разработки Вредоносного ПО (Софта На Игру / Рат с++)",
    "Для Dox'a/Osint'a",
    "Ролка",
    "Запрещенка"
]

def ensure_categories():
    for net in NEURAL_NETS:
        if net not in PROMPTS_DATA:
            PROMPTS_DATA[net] = {}
        for style in STYLES:
            if style not in PROMPTS_DATA[net]:
                PROMPTS_DATA[net][style] = {}
            for cat in DEFAULT_CATEGORIES:
                if cat not in PROMPTS_DATA[net][style]:
                    PROMPTS_DATA[net][style][cat] = []

ensure_categories()

async def neural_net_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    buttons = [[InlineKeyboardButton(name, callback_data=f"lib|style|{name}")] for name in NEURAL_NETS]
    buttons.append([back_button(lang, "menu|main")])
    await query.edit_message_text(get_text(lang, "choose_neural_net"), reply_markup=InlineKeyboardMarkup(buttons))

async def style_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    net = query.data.split("|")[-1]
    context.user_data["lib_net"] = net
    buttons = [[InlineKeyboardButton(style, callback_data=f"lib|category|{net}|{style}|1")] for style in STYLES]
    buttons.append([back_button(lang, "menu|library")])
    await query.edit_message_text(get_text(lang, "choose_style", net), reply_markup=InlineKeyboardMarkup(buttons))

async def category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    parts = query.data.split("|")
    net, style, page = parts[2], parts[3], int(parts[4])
    context.user_data["lib_net"] = net
    context.user_data["lib_style"] = style

    categories = list(PROMPTS_DATA[net][style].keys())
    total_pages = math.ceil(len(categories) / ITEMS_PER_PAGE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_cats = categories[start:end]
    context.user_data["lib_categories"] = categories

    buttons = [[InlineKeyboardButton(cat, callback_data=f"lib|prompts|{net}|{style}|{idx}|1")] for idx, cat in enumerate(page_cats, start=start)]
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"lib|category|{net}|{style}|{page-1}"))
    if page < total_pages:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"lib|category|{net}|{style}|{page+1}"))
    if nav:
        buttons.append(nav)
    buttons.append([back_button(lang, f"lib|style|{net}")])
    await query.edit_message_text(get_text(lang, "categories_page", net, style, page, total_pages), reply_markup=InlineKeyboardMarkup(buttons))

async def prompts_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    parts = query.data.split("|")
    net, style, cat_idx, page = parts[2], parts[3], int(parts[4]), int(parts[5])
    context.user_data["lib_net"] = net
    context.user_data["lib_style"] = style

    categories = context.user_data.get("lib_categories", [])
    if cat_idx >= len(categories):
        await query.answer("Error", show_alert=True)
        return
    category = categories[cat_idx]
    context.user_data["lib_category"] = category

    prompts = PROMPTS_DATA[net][style][category]
    total_pages = math.ceil(len(prompts) / ITEMS_PER_PAGE) if prompts else 1
    page = max(1, min(page, total_pages))
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_prompts = prompts[start:end] if prompts else []

    user = await get_user(query.from_user.id)
    premium = user[4] if user else 0
    balance = user[6] if user else 0

    buttons = []
    for i, prompt in enumerate(page_prompts):
        idx = start + i + 1
        title = prompt["title"]
        price = prompt.get("price", 0)
        premium_only = prompt.get("premium_only", False)
        label = title
        if premium_only and not premium:
            label += " 🔒"
        elif price > 0:
            label += f" 💰{price}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"lib|detail|{net}|{style}|{category}|{idx}")])

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"lib|prompts|{net}|{style}|{cat_idx}|{page-1}"))
    if page < total_pages:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"lib|prompts|{net}|{style}|{cat_idx}|{page+1}"))
    if nav:
        buttons.append(nav)
    buttons.append([back_button(lang, f"lib|category|{net}|{style}|1")])
    await query.edit_message_text(get_text(lang, "prompts_page", net, style, category, page, total_pages), reply_markup=InlineKeyboardMarkup(buttons))

async def prompt_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    parts = query.data.split("|")
    net, style, category, num_str = parts[2], parts[3], parts[4], parts[5]
    num = int(num_str) - 1
    prompt = PROMPTS_DATA[net][style][category][num]
    title = prompt["title"]
    text = prompt["text"]
    price = prompt.get("price", 0)
    premium_only = prompt.get("premium_only", False)
    prompt_id = f"{net}|{style}|{category}|{num+1}"

    user = await get_user(query.from_user.id)
    premium = user[4] if user else 0
    balance = user[6] if user else 0
    purchased = await has_purchased(query.from_user.id, prompt_id)

    buttons = []
    if premium_only and not premium:
        buttons.append([InlineKeyboardButton(get_text(lang, "subscription_required"), callback_data="none")])
    elif price > 0 and not purchased:
        if balance >= price:
            buttons.append([InlineKeyboardButton(get_text(lang, "buy_prompt", price=price), callback_data=f"lib|buy|{net}|{style}|{category}|{num+1}")])
        else:
            buttons.append([InlineKeyboardButton(get_text(lang, "not_enough_coins"), callback_data="none")])

    favs = await get_favorites(query.from_user.id)
    if prompt_id in favs:
        buttons.append([InlineKeyboardButton(get_text(lang, "remove_fav"), callback_data=f"fav|remove|{prompt_id}")])
    else:
        buttons.append([InlineKeyboardButton(get_text(lang, "add_fav"), callback_data=f"fav|add|{prompt_id}")])

    cat_idx = context.user_data.get("lib_categories", []).index(category) if category in context.user_data.get("lib_categories", []) else 0
    buttons.append([back_button(lang, f"lib|prompts|{net}|{style}|{cat_idx}|1")])

    await query.edit_message_text(f"**{title}**\n\n{text}", reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

async def buy_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    parts = query.data.split("|")
    net, style, category, num_str = parts[2], parts[3], parts[4], parts[5]
    num = int(num_str) - 1
    prompt = PROMPTS_DATA[net][style][category][num]
    price = prompt.get("price", 0)
    user_id = query.from_user.id
    user = await get_user(user_id)
    balance = user[6] if user else 0

    if balance < price:
        await query.answer(get_text(lang, "not_enough_coins"), show_alert=True)
        return

    await update_user_balance(user_id, -price)
    prompt_id = f"{net}|{style}|{category}|{num+1}"
    await add_purchased(user_id, prompt_id)
    await query.answer(get_text(lang, "prompt_purchased"), show_alert=True)
    await prompt_detail(update, context)

async def toggle_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ru")
    parts = query.data.split("|")
    action = parts[1]
    prompt_id = "|".join(parts[2:])
    user_id = query.from_user.id
    if action == "add":
        await add_favorite(user_id, prompt_id)
        await query.answer(get_text(lang, "prompt_added_fav"), show_alert=True)
    elif action == "remove":
        await remove_favorite(user_id, prompt_id)
        await query.answer(get_text(lang, "prompt_removed_fav"), show_alert=True)
    await prompt_detail(update, context)