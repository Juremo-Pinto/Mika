from collections.abc import Mapping
from Modules.settings._base import BaseSettings
import os, json, resources_path, weakref
from typing import Any, Dict

SETTINGS_PATH = resources_path.SETTINGS

class Settings(BaseSettings):
    _instances = weakref.WeakSet()
    default_structure = {}
    
    def __init__(self, name: str, section: str = None):
        """
        Initialize a Settings instance.
        
        Args:
            name (str): The name of the settings file (without extension) to load or create.
            section (str, optional): Folder path inside the SETTINGS directory where this
                file will be stored. Can be nested (e.g., "tts/langs"). Defaults to root.
        """
        
        super().__init__(name, section)
        
        Settings._instances.add(self)
    
    
    @classmethod
    def reload(cls):
        for instance in cls._instances:
            instance.apply_default_structure()
    
    
    def apply_default_structure(self):
        self.load()
        
        for key, value in self.default_structure.items():
            self._data.setdefault(key, value)
        
        self.save()
    
    
    def setup(self, **default_structure):
        self.default_structure = default_structure
        self.apply_default_structure()