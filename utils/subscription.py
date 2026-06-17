from telegram import Bot
from config import CHANNEL_ID

async def is_subscribed(bot: Bot, user_id: int) -> bool:
    """
    Проверяет, подписан ли пользователь на канал.
    Возвращает True, если статус участника не 'left' и не 'kicked'.
    """
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status not in ["left", "kicked"]
    except Exception:
        # Если бот не может проверить (не админ, канал не найден) — считаем, что не подписан
        return False