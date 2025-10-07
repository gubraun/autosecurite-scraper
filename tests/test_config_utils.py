import unittest
from utils.config_utils import load_config

class TestConfigUtils(unittest.TestCase):
    def test_load_config(self):
        config = load_config()
        self.assertIn("DEFAULT", config)
        self.assertIn("TELEGRAM", config)
        self.assertTrue(config["DEFAULT"].get("URL"))
        self.assertTrue(config["TELEGRAM"].get("ENABLED"))

if __name__ == "__main__":
    unittest.main()
