from project import *


class Config:
    """Загружает настройки из файла"""

    CONFIG_PATH = "config.json"

    def __init__(self):
        cfg = self._load_config()
        self.login = cfg["login"]
        self.password = cfg["password"]
        self.pairs = cfg["pairs"]
        self.confirmation_interval_min = cfg["confirmation_interval_min"]
        logging.debug("config is initialized")

    def _load_config(self):
        with open(self.CONFIG_PATH, 'r') as f:
            conf = json.load(f)
            assert type(conf) is dict
            return conf


if __name__ == '__main__':
    pass
