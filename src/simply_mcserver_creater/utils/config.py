import json
import os

from PyQt5.QtCore import QObject, pyqtSignal


class Config(QObject):
    # server_type: str
    dark_mode: bool
    theme_color: str
    language: str
    log_level: str
    use_proxy: bool

    showDepartureChanged = pyqtSignal(bool)

    def __init__(self, **kwargs):
        super().__init__()
        # self.server_type = kwargs.get('server_type', 'Release')
        self.dark_mode = kwargs.get('dark_mode', False)
        self.theme_color = kwargs.get('theme_color', '#009FAA')
        self.language = kwargs.get('language', 'en-US')
        self.log_level = kwargs.get('log_level', 'INFO')
        self.use_proxy = kwargs.get('use_proxy', False)

    @classmethod
    def load(cls):
        if not os.path.exists('config.json'):
            rt = cls()
        else:
            with open('config.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            rt = cls(**data)
        rt.save()
        return rt

    @property
    def dict(self):
        return {
            # 'server_type': self.server_type,
            'dark_mode': self.dark_mode,
            'theme_color': self.theme_color,
            'language': self.language,
            'log_level': self.log_level,
            'use_proxy': self.use_proxy,
        }

    def save(self):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.dict, f, indent=4, ensure_ascii=False)


config = Config.load()
