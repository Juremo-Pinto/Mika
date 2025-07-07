from typing import Any, Dict, List
from discord import VoiceClient


_UNWANTED_JSON_KEYS = ["formats", "thumbnails", "thumbnail", "automatic_captions", "heatmap", "requested_formats", "subtitles", "description"]
_SHUFFLE_KEYWORDS = ["aleatorio", "shuffle", "embaralha", "embaraia", "embaralhado", "embaraiado"]


async def get_voice_channel_id(voice_client: VoiceClient | None) -> int | None:
    return voice_client.channel.id if voice_client else None


async def is_shuffle(command_list: List[str]) -> bool:
    return any(keyword == command.lower() for command in command_list for keyword in _SHUFFLE_KEYWORDS)


async def is_playlist(url: str) -> bool:
    root_url = url.split('?')[0]
    return root_url == "https://www.youtube.com/playlist"


async def remove_url_parameters(full_url: str) -> str:
    return full_url.split('&')[0]


async def clean_info(info: Dict[str, Any]) -> Dict[str, Any]:
    for key in _UNWANTED_JSON_KEYS:
        if key in info:
            del info[key]
    
    return info