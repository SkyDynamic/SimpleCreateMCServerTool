import json
import os


class VanillaServerManager:
    def __init__(self):
        ...

    def save_to_file(self, path=None, data=None, server_type="Release"):
        if not os.path.exists('serverData'):
            os.mkdir('serverData')
        path = f'serverData/vanilla{server_type}ServerDate.json' if path is None else path
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_from_file(self, server_type="Release"):
        if not os.path.exists(f'serverData/vanilla{server_type}ServerDate.json'):
            return
        path = f'serverData/vanilla{server_type}ServerDate.json'
        with open(path, 'r', encoding='utf8') as f:
            return json.load(f)

class FabricServerManager:
    def __init__(self):
        ...

    def save_to_file(self, path=None, data=None, server_type="Release"):
        if not os.path.exists('serverData'):
            os.mkdir('serverData')
        path = f'serverData/fabric{server_type}ServerDate.json' if path is None else path
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def save_loader_or_installer(self, data, type):
        if not os.path.exists('serverData'):
            os.mkdir('serverData')
        path = f'serverData/fabric{type}Date.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_from_file(self, server_type="Release"):
        if not os.path.exists(f'serverData/fabric{server_type}ServerDate.json'):
            return
        path = f'serverData/fabric{server_type}ServerDate.json'
        with open(path, 'r', encoding='utf8') as f:
            return json.load(f)