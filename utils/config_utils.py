import configparser
CONFIG_PATH = "config.ini"

def load_config():
    """
    Loads configuration from CONFIG_PATH.
    Returns:
        ConfigParser object with loaded configuration.
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config
