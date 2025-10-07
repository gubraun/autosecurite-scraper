import unittest
from datetime import datetime
from utils.config_utils import load_config
from utils.storage_utils import save_current_dates
from scrape import should_send_telegram

class TestShouldSendTelegram(unittest.TestCase):
    def setUp(self):
        self.config = load_config()
        # Save a known last_dates.json
        save_current_dates({datetime(2025, 10, 14, 12, 45)})

    def test_force_notify(self):
        self.config["TELEGRAM"]["FORCE_NOTIFY"] = "true"
        result = should_send_telegram([datetime(2025, 10, 15, 8, 0)], self.config)
        self.assertTrue(result)
        self.config["TELEGRAM"]["FORCE_NOTIFY"] = "false"

    def test_new_dates(self):
        result = should_send_telegram([datetime(2025, 10, 16, 8, 0)], self.config)
        self.assertTrue(result)

    def test_no_new_dates(self):
        result = should_send_telegram([datetime(2025, 10, 14, 12, 45)], self.config)
        self.assertTrue(result)  # Should send if no scheduled_date and NOTIFY_ONLY_IF_EARLIER is false

if __name__ == "__main__":
    unittest.main()
