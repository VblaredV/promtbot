WIDE_CHAR = "\u2800"

def wide_button(text: str, count: int = 12) -> str:
    pad = WIDE_CHAR * count
    return f"{pad}{text}{pad}"

TEXTS = {
    "ru": {
        # Старт / подписка
        "start_welcome": "👋 Привет! Для использования бота подпишитесь на канал: {channel}",
        "check_subscribe": "✅ Проверить подписку",
        "choose_lang": "🌐 Выберите язык / Choose language:",
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        "not_subscribed": "❌ Вы не подписаны на канал.",
        "welcome_menu": "🏠 Главное меню:",
        "banned_user": "⛔ Вы заблокированы.",

        # Главное меню
        "menu_library": "📚 Библиотека",
        "menu_search": wide_button("🔍 Поиск промтов", 1),
        "menu_profile": wide_button("👤 Профиль", 10),
        "menu_shop": wide_button("🛍️ Магазин", 10),
        "menu_admin": wide_button("⚙️ Админ-панель", 10),
        "back": wide_button("⬅️ Назад", 10),

        # Библиотека
        "choose_neural_net": "🤖 Выбери нейросеть:",
        "choose_style": "{} — выбери стиль:",
        "categories_page": "{} > {} — категории (стр. {}/{} )",
        "prompts_page": "{} > {} > {} (стр. {}/{})",
        "subscription_required": "🔐 Требуется подписка",
        "buy_prompt": "🪙 Купить за {price} монет",
        "not_enough_coins": "😔 Недостаточно монет для покупки.",
        "prompt_purchased": "✅ Промт куплен!",
        "prompt_added_fav": "⭐ Добавлено в избранное",
        "prompt_removed_fav": "🗑️ Удалено из избранного",
        "add_fav": "⭐ В избранное",
        "remove_fav": "❌ Удалить из избранного",

        # Поиск
        "search_start": "🔍 Выбери нейросеть для поиска:",
        "search_style": "{} — выбери стиль:",
        "search_category": "{} > {} — выбери категорию:",
        "search_input": "✏️ Введи ключевые слова для поиска:",
        "search_no_results": "🔍 Ничего не найдено.",

        # Профиль
        "profile_info": (
            "Ваш уникальный ID: {unique_id}\n"
            "Username: @{username}\n"
            "Язык: {language}\n"
            "Подписка до: {subscription_until}\n"
            "Баланс: {balance} монет\n"
            "Уведомления: {notifications}"
        ),
        "notifications_on": "вкл",
        "notifications_off": "выкл",
        "notifications_on_btn": "🔔 Уведомления: вкл",
        "notifications_off_btn": "🔔 Уведомления: выкл",
        "favorites_empty": "📭 Избранных промтов пока нет.",
        "fav_title": "⭐ Твои избранные промты:",
        "withdraw_request": "Запросить вывод",
        "username_none": "нет",
        "language_rus": "Русский",
        "language_eng": "English",
        "subscription_none": "нет",
        "profile_not_found": "Профиль не найден.",
        "fav_btn": "⭐ Избранное",
        "referral_btn": "🤝 Реферальная система",
        "change_lang_btn": "🌐 Сменить язык",

        # Реферальная система
        "referral_title": "🤝 Реферальная система",
        "referral_text": (
            "📰 Приглашайте друзей и зарабатывайте:\n"
            "└ Вам 69 монет за друга, запустившего бота\n"
            "└ 40% от пополнений рефералов\n"
            "└ Другу 69 монет на старт\n"
            "🔗 Ваша ссылка: {ref_link}\n"
            "📊 Статистика:\n"
            "Приглашено: {invited}\n"
            "Активно: {active}\n"
            "Купили подписку: {subscribed}\n"
            "Заработок: {earned} монет\n"
            "Доступно к выводу: {available} монет\n"
            "Выведено: {withdrawn} монет"
        ),

        # Магазин
        "shop_coins": "💎 Купить монеты",
        "shop_subscription": "🔓 Купить подписку",
        "select_package": "Выбери пакет монет:",
        "buy_coins_package": "🪙 {} монет ({} ⭐)",
        "payment_info": "💳 Для покупки {} монет отправь {} звёзд на канал {} или используй другой метод. После оплаты нажми «Я оплатил».",
        "payment_done": "💸 Я оплатил",
        "balance_updated": "✅ Баланс пополнен на {} монет!",
        "subscription_activated": "🎉 Подписка активирована на 30 дней!",
        "subscription_not_enough": "😔 Недостаточно монет. Нужно 552.",
        "current_balance": "💰 Баланс: {} монет",
        "payment_instructions": (
            "💳 Выберите способ оплаты:\n"
            "1. Telegram Stars\n"
            "2. СБП\n"
            "3. FanPay\n\n"
            "После оплаты нажмите «Я оплатил» и укажите сумму/скриншот."
        ),

        # Админка
        "admin_menu_title": "🛠 Админ-панель",
        "admin_search_prompt": "Введите уникальный ID пользователя:",
        "admin_ban_prompt": "Введите уникальный ID пользователя для бана/разбана:",
        "admin_msg_prompt": "Введите уникальный ID получателя:",
        "admin_msg_text_prompt": "Введите текст сообщения:",
        "admin_balance_prompt": "Введите уникальный ID пользователя:",
        "admin_balance_amount_prompt": "Введите сумму (отрицательное число для списания):",
        "admin_premium_prompt": "Введите уникальный ID пользователя для выдачи премиума:",
        "admin_addprompt_net": "Выбери нейросеть:",
        "admin_addprompt_style": "{} — выбери стиль:",
        "admin_addprompt_cat": "Введи название категории (можно новую):",
        "admin_addprompt_text": "Отправь текст промта (или .txt файл). Первая строка станет заголовком.",
        "admin_addprompt_price": "Введи цену (0 или кратно 69):",
        "admin_addprompt_premium": "Только с подпиской? (1 — да, 0 — нет):",
        "admin_prompt_saved": "📥 Промт добавлен! (Рассылка пока не реализована.)",
        "admin_user_not_found": "🔍 Пользователь не найден.",
        "admin_ban_success": "🚫 Пользователь заблокирован.",
        "admin_unban_success": "✅ Пользователь разблокирован.",
        "admin_premium_granted": "⭐ Премиум выдан навсегда.",
        "admin_coins_updated": "💰 Баланс обновлён.",
        "admin_message_sent": "✉️ Сообщение отправлено.",
        "admin_balance_result": "💰 Баланс обновлён. Текущий баланс: {} монет.",
        "admin_msg_sent": "✅ Сообщение отправлено.",
        "admin_premium_result": "⭐ Премиум выдан навсегда.",
        "important_msg": "⚠️ Важное",
        "normal_msg": "ℹ️ Обычное",
        "choose_importance": "Выберите важность сообщения:",
        "notification_disabled_normal": "❌ У пользователя выключены уведомления. Обычное сообщение не отправлено.",
        "admin_msg_important_prefix": "⚠️ Важное сообщение",
        "admin_msg_normal_prefix": "ℹ️ Сообщение",
        "admin_msg_from": "от администратора",
        "admin_msg_send_error": "⚠️ Ошибка отправки: {error}",
        "admin_enter_number": "⚠️ Введите целое число.",
        "error": "⚠️ Произошла ошибка. Попробуйте позже.",
    },

    "en": {
        # Start / subscription
        "start_welcome": "👋 Hello! Please subscribe to the channel: {channel}",
        "check_subscribe": "✅ Check subscription",
        "choose_lang": "🌐 Choose language:",
        "lang_ru": "🇷🇺 Russian",
        "lang_en": "🇬🇧 English",
        "not_subscribed": "❌ You are not subscribed to the channel.",
        "welcome_menu": "🏠 Main menu:",
        "banned_user": "⛔ You are banned.",

        # Main menu
        "menu_library": "📚 Library",
        "menu_search": wide_button("🔍 Search Prompts", 1),
        "menu_profile": wide_button("👤 Profile", 10),
        "menu_shop": wide_button("🛍️ Shop", 10),
        "menu_admin": wide_button("⚙️ Admin Panel", 10),
        "back": wide_button("⬅️ Back", 10),

        # Library
        "choose_neural_net": "🤖 Choose a neural network:",
        "choose_style": "{} — choose style:",
        "categories_page": "{} > {} — categories (page {}/{})",
        "prompts_page": "{} > {} > {} (page {}/{})",
        "subscription_required": "🔐 Subscription required",
        "buy_prompt": "🪙 Buy for {price} coins",
        "not_enough_coins": "😔 Not enough coins to buy.",
        "prompt_purchased": "✅ Prompt purchased!",
        "prompt_added_fav": "⭐ Added to favorites",
        "prompt_removed_fav": "🗑️ Removed from favorites",
        "add_fav": "⭐ Add to favorites",
        "remove_fav": "❌ Remove from favorites",

        # Search
        "search_start": "🔍 Choose a neural network for search:",
        "search_style": "{} — choose style:",
        "search_category": "{} > {} — choose category:",
        "search_input": "✏️ Enter keywords to search:",
        "search_no_results": "🔍 Nothing found.",

        # Profile
        "profile_info": (
            "Your unique ID: {unique_id}\n"
            "Username: @{username}\n"
            "Language: {language}\n"
            "Subscription until: {subscription_until}\n"
            "Balance: {balance} coins\n"
            "Notifications: {notifications}"
        ),
        "notifications_on": "on",
        "notifications_off": "off",
        "notifications_on_btn": "🔔 Notifications: ON",
        "notifications_off_btn": "🔔 Notifications: OFF",
        "favorites_empty": "📭 No favorites yet.",
        "fav_title": "⭐ Your favorite prompts:",
        "withdraw_request": "Request withdrawal",
        "username_none": "none",
        "language_rus": "Russian",
        "language_eng": "English",
        "subscription_none": "none",
        "profile_not_found": "Profile not found.",
        "fav_btn": "⭐ Favorites",
        "referral_btn": "🤝 Referral System",
        "change_lang_btn": "🌐 Change Language",

        # Referral system
        "referral_title": "🤝 Referral System",
        "referral_text": (
            "📰 Invite friends and earn:\n"
            "└ 69 coins per friend starting the bot\n"
            "└ 40% from referrals' top-ups\n"
            "└ Friend gets 69 coins at start\n"
            "🔗 Your link: {ref_link}\n"
            "📊 Stats:\n"
            "Invited: {invited}\n"
            "Active: {active}\n"
            "Subscribed: {subscribed}\n"
            "Earnings: {earned} coins\n"
            "Available for withdrawal: {available} coins\n"
            "Withdrawn: {withdrawn} coins"
        ),

        # Shop
        "shop_coins": "💎 Buy Coins",
        "shop_subscription": "🔓 Buy Subscription",
        "select_package": "Choose a coin package:",
        "buy_coins_package": "🪙 {} coins ({} ⭐)",
        "payment_info": "💳 To buy {} coins send {} stars to {} or use another method. After payment press 'I paid'.",
        "payment_done": "💸 I paid",
        "balance_updated": "✅ Balance topped up by {} coins!",
        "subscription_activated": "🎉 Subscription activated for 30 days!",
        "subscription_not_enough": "😔 Not enough coins. Need 552.",
        "current_balance": "💰 Balance: {} coins",
        "payment_instructions": (
            "💳 Select payment method:\n"
            "1. Telegram Stars\n"
            "2. SBP\n"
            "3. FanPay\n\n"
            "After payment press 'I paid' and provide amount/screenshot."
        ),

        # Admin panel
        "admin_menu_title": "🛠 Admin Panel",
        "admin_search_prompt": "Enter user's unique ID:",
        "admin_ban_prompt": "Enter user's unique ID to ban/unban:",
        "admin_msg_prompt": "Enter recipient's unique ID:",
        "admin_msg_text_prompt": "Enter message text:",
        "admin_balance_prompt": "Enter user's unique ID:",
        "admin_balance_amount_prompt": "Enter amount (negative to deduct):",
        "admin_premium_prompt": "Enter user's unique ID to grant premium:",
        "admin_addprompt_net": "Choose neural network:",
        "admin_addprompt_style": "{} — choose style:",
        "admin_addprompt_cat": "Enter category name (can be new):",
        "admin_addprompt_text": "Send prompt text (or .txt file). First line will be the title.",
        "admin_addprompt_price": "Enter price (0 or multiple of 69):",
        "admin_addprompt_premium": "Only with subscription? (1 — yes, 0 — no):",
        "admin_prompt_saved": "📥 Prompt added! (Broadcast not implemented yet.)",
        "admin_user_not_found": "🔍 User not found.",
        "admin_ban_success": "🚫 User banned.",
        "admin_unban_success": "✅ User unbanned.",
        "admin_premium_granted": "⭐ Premium granted forever.",
        "admin_coins_updated": "💰 Balance updated.",
        "admin_message_sent": "✉️ Message sent.",
        "admin_balance_result": "💰 Balance updated. Current balance: {} coins.",
        "admin_msg_sent": "✅ Message sent.",
        "admin_premium_result": "⭐ Premium granted forever.",
        "important_msg": "⚠️ Important",
        "normal_msg": "ℹ️ Normal",
        "choose_importance": "Select message importance:",
        "notification_disabled_normal": "❌ User has notifications disabled. Normal message not sent.",
        "admin_msg_important_prefix": "⚠️ Important message",
        "admin_msg_normal_prefix": "ℹ️ Message",
        "admin_msg_from": "from administrator",
        "admin_msg_send_error": "⚠️ Send error: {error}",
        "admin_enter_number": "⚠️ Enter an integer.",
        "error": "⚠️ An error occurred. Please try again later.",
    }
}

def get_text(lang, key, **kwargs):
    text = TEXTS.get(lang, {}).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text