import unittest
from utils.date_utils import month_mapping

class TestDateUtils(unittest.TestCase):
    def test_months_german(self):
        self.assertEqual(month_mapping["januar"], 1)
        self.assertEqual(month_mapping["dezember"], 12)
    def test_months_french(self):
        self.assertEqual(month_mapping["janvier"], 1)
        self.assertEqual(month_mapping["décembre"], 12)
        self.assertEqual(month_mapping["aout"], 8)
        self.assertEqual(month_mapping["fevrier"], 2)

if __name__ == "__main__":
    unittest.main()
