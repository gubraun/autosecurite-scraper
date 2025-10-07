import unittest
from datetime import datetime
import os
import json
from utils.storage_utils import load_last_dates, save_current_dates, LAST_DATES_PATH

class TestStorageUtils(unittest.TestCase):
    def setUp(self):
        # Backup existing file if present
        if os.path.exists(LAST_DATES_PATH):
            os.rename(LAST_DATES_PATH, LAST_DATES_PATH + ".bak")

    def tearDown(self):
        # Remove test file
        if os.path.exists(LAST_DATES_PATH):
            os.remove(LAST_DATES_PATH)
        # Restore backup
        if os.path.exists(LAST_DATES_PATH + ".bak"):
            os.rename(LAST_DATES_PATH + ".bak", LAST_DATES_PATH)

    def test_save_and_load_dates(self):
        dates = {datetime(2025, 10, 14, 12, 45), datetime(2025, 11, 1, 8, 0)}
        save_current_dates(dates)
        loaded = load_last_dates()
        self.assertEqual(dates, loaded)

    def test_load_empty(self):
        if os.path.exists(LAST_DATES_PATH):
            os.remove(LAST_DATES_PATH)
        loaded = load_last_dates()
        self.assertEqual(loaded, set())

if __name__ == "__main__":
    unittest.main()
