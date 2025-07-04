from collections.abc import Mapping
import os, json, resources_path, weakref
from typing import Any, Dict

SETTINGS_PATH = resources_path.SETTINGS

class Settings(Mapping):
    _instances = weakref.WeakSet()
    
    def __init__(self, name: str):
        """
        Initialize a Settings instance.does
        
        Args:
            name (str): The name of the settings file (without extension) to load or create.
        """
        self.name = name
        self.path = self.get_path()
        
        self._data = {}
        
        if not os.path.exists(self.path):
            self.create_file()
        else:
            self.load()
        
        Settings._instances.add(self)
    
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)
    
    
    @classmethod
    def reload(cls):
        for instance in cls._instances:
            instance.load()
    
    
    def get_path(self) -> str:
        filename = f"{self.name.lower()}.json"
        return os.path.join(SETTINGS_PATH, filename)
    
    
    def create_file(self):
        os.makedirs(SETTINGS_PATH, exist_ok=True) 
        with open(self.path, 'x', encoding='utf-8') as f:
            json.dump({}, f)
    
    
    def save(self):
        with open(self.path, "w", encoding='utf-8') as f:
            json.dump(self._data, f, indent=4, ensure_ascii=True)
    
    def load(self):
        with open(self.path, "r", encoding='utf-8') as f:
            self._data = json.load(f)
    
    
    def setup(self, **default_structure):
        self.load()
        
        for key, value in default_structure.items():
            self._data.setdefault(key, value)
        
        self.save()