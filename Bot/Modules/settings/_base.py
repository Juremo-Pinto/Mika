from collections.abc import Mapping
import os, json, resources_path
from typing import Any, Dict

SETTINGS_PATH = resources_path.SETTINGS


class BaseSettings(Mapping):
    def __init__(self, name: str, section: str = None):
        self.section = section
        self.name = name
        
        self.folder, self.full_path = self.get_path()
        
        self._data = {}
        
        if not os.path.exists(self.full_path):
            self.create_file()
        else:
            self.load()
    
    
    def __hash__(self):
        return hash(id(self))
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)
    
    def get_path(self) -> str:
        filename = f"{self.name.lower()}.json"
        
        folder = os.path.join(SETTINGS_PATH, self.section) if self.section else SETTINGS_PATH
        full_path = os.path.join(folder, filename)
        
        return folder, full_path
    
    def create_file(self):
        os.makedirs(self.folder, exist_ok=True) 
        with open(self.full_path, 'x', encoding='utf-8') as f:
            json.dump({}, f)
    
    
    def create_if_not_exists(self):
        if not os.path.exists(self.full_path):
            self.create_file()
    
    
    def save(self):
        self.create_if_not_exists()
        
        with open(self.full_path, "w", encoding='utf-8') as f:
            json.dump(self._data, f, indent=4, ensure_ascii=True)
    
    def load(self):
        self.create_if_not_exists()
        
        with open(self.full_path, "r", encoding='utf-8') as f:
            self._data = json.load(f)

