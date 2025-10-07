import telegram

async def send_telegram_message(token, chat_id, message):
    """
    Sends a message via Telegram bot.
    Args:
        token: Telegram bot token string.
        chat_id: Telegram chat ID string.
        message: Message string to send.
    """
    bot = telegram.Bot(token=token)
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.constants.ParseMode.HTML)
    except Exception as e:
        print(f"Telegram error: {e}")
