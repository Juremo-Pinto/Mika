import os, json, resources_path
from typing import Any, Dict
from discord import Enum


class SettingType(Enum):
    DEBUG = 0
    BOT = 1
    MISCHIEF = 2

SETTINGS_PATH = resources_path.SETTINGS


class Settings(dict):
    def __init__(self, setting_type: SettingType):
        self.setting_type = setting_type
        self.path = self.get_path()
        
        if not os.path.exists(self.path):
            Settings.create_settings()
        
        super().__init__()
    
    
    def get_path(self) -> str:
        filename = f"{self.setting_type.name.lower()}.json"
        return os.path.join(SETTINGS_PATH, filename)
    
    
    @staticmethod
    def create_file(filename: str):
        path = os.path.join(SETTINGS_PATH, filename)
        
        if not os.path.exists(path):
            os.makedirs(SETTINGS_PATH, exist_ok=True) 
            
            with open(path, 'x', encoding='utf-8') as f:
                json.dump({}, f)
    
    
    @staticmethod
    def create_settings():
        for setting in SettingType:
            Settings.create_file(f"{setting.name.lower()}.json")
    
    
    def save(self):
        with open(self.path, "w", encoding='utf-8') as f:
            json.dump(self, f)
        
    def load(self):
        with open(self.path, "w", encoding='utf-8') as f:
            self = json.load(f)
    
    
    def setup(self, default_structure = Dict[str, Any]):
        for key in default_structure:
            if key not in self:
                self[key] = default_structure[key]
        
        self.save()
        