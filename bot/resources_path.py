# resource_path.py

import os

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

AUDIOS = os.path.join(BASE_PATH, "resources", "audios")
IMAGES = os.path.join(BASE_PATH, "resources", "images")
DATABASES = os.path.join(BASE_PATH, "resources", "database")
TEXTS = os.path.join(BASE_PATH, "resources", "text")
CACHE = os.path.join(BASE_PATH, "resources", "cache")
SETTINGS = os.path.join(BASE_PATH, "resources", "settings")
LOCK = os.path.join(BASE_PATH, "resources")