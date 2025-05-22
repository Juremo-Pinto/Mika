import os

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

path_to_audios = os.path.join(base_path, "Bot", "Resources", "Audios")
path_to_images = os.path.join(base_path, "Bot", "Resources", "Images")
path_to_databases = os.path.join(base_path, "Bot", "Resources", "DataBase")
path_to_texts = os.path.join(base_path, "Bot", "Resources", "Text")
path_to_cache = os.path.join(base_path, "Bot", "Resources", "Cache")
path_to_lock = os.path.join(base_path, "Bot", "Resources")


def resources_path(type):
    match type.lower():
        case "audios" | "audio":
            return path_to_audios
        case "images" | "image":
            return path_to_images
        case "databases" | "database":
            return path_to_databases
        case "texts" | "text":
            return path_to_texts
        case "cache":
            return path_to_cache
        case "lock":
            return path_to_lock
        case _:
            raise ValueError(f"Resource type {type} is not recognized")