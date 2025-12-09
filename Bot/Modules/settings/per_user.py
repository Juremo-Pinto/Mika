import os
from Modules.settings._base import BaseSettings


class UserSettings(BaseSettings):
    default_structure = {}
    
    def __init__(self, name, section = None):
        section = os.path.join('user', section) if section is not None else 'user'
        
        super().__init__(name, section)
    
    def set_structure(self, **def_structure):
        self.default_structure = def_structure
    
    def setup_user(self, user_id):
        self.load()
        
        self._data.setdefault(user_id, {})
        
        for key, value in self.default_structure.items():
            self._data[user_id].setdefault(key, value)
        
        self.save()
    
    def setup_if_not_exists(self, user_id):
        if user_id not in self._data.keys():
            self.setup_user(user_id)
    
    
    def get_for_user(self, user_id, key):
        self.setup_if_not_exists(user_id)
        
        return self._data[user_id][key]
    
    
    def set_for_user(self, user_id, key, value, *, auto_save = True):
        self.setup_if_not_exists(user_id)
        
        self._data[user_id][key] = value
        
        if auto_save:
            self.save()