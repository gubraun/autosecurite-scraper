import unittest
from unittest.mock import patch, AsyncMock
from utils.telegram_utils import send_telegram_message

class TestTelegramUtils(unittest.IsolatedAsyncioTestCase):
    @patch("utils.telegram_utils.telegram.Bot")
    async def test_send_telegram_message(self, mock_bot):
        mock_instance = mock_bot.return_value
        mock_instance.send_message = AsyncMock()
        await send_telegram_message("dummy_token", "dummy_chat_id", "Test message")
        mock_instance.send_message.assert_awaited_once()

if __name__ == "__main__":
    unittest.main()
