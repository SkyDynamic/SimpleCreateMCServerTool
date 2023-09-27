import json
import os

from PyQt5.QtCore import QObject


class Config(QObject):
    show_snapshot: bool
    dark_mode: bool
    theme_color: str
    language: str
    log_level: str

    def __init__(self, **kwargs):
        super().__init__()
        self.show_snapshot = kwargs.get('show_snapshot', False)
        self.dark_mode = kwargs.get('dark_mode', False)
        self.theme_color = kwargs.get('theme_color', '#009FAA')
        self.language = kwargs.get('language', 'en-US')
        self.log_level = kwargs.get('log_level', 'INFO')

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
            'show_snapshot': self.show_snapshot,
            'dark_mode': self.dark_mode,
            'theme_color': self.theme_color,
            'language': self.language,
            'log_level': self.log_level
        }

    def save(self):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.dict, f, indent=4, ensure_ascii=False)


config = Config.load()
