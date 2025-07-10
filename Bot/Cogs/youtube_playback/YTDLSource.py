import asyncio
from typing import Any, Dict, Optional, Self

from discord import AudioSource, PCMVolumeTransformer, FFmpegPCMAudio

from concurrent.futures import ThreadPoolExecutor
from Cogs.youtube_playback.YTDLConfig import *

from yt_dlp import YoutubeDL

THREAD_EXECUTOR = ThreadPoolExecutor(max_workers=9)

class YTDLSource(PCMVolumeTransformer):
    def __init__(self, source: AudioSource, *, data: Dict[str, Any], volume: float=0.5):
        super().__init__(source, volume)
        
        self.data = data
        
        self.title: str = data.get('title')
        self.url = ""
    
    
    @staticmethod
    def extract(extractor: YoutubeDL, url: str, download: bool) -> Any | dict[str, Any] | None:
        return extractor.extract_info(url, download=download)
    
    
    @staticmethod
    async def wait_for_extraction(loop: asyncio.AbstractEventLoop, extractor: YoutubeDL, url: str, download: bool, timeout: int):
        return await asyncio.wait_for(
            loop.run_in_executor(THREAD_EXECUTOR , YTDLSource.extract, extractor, url, download),
            timeout=timeout
            )
    
    
    @classmethod
    async def stream_from_url(cls, url: str, *, timeout: int = 30, loop: Optional[asyncio.AbstractEventLoop] = None) -> Self:
        loop = loop or asyncio.get_event_loop()
        
        data = await cls.wait_for_extraction(loop, yt_downloader, url=url, download=False, timeout=timeout)
        filename: str = data['url']
        
        return cls(FFmpegPCMAudio(filename, **ffmpeg_format_options), data=data)
    
    
    @classmethod
    async def get_info_from_url(cls, url: str, *, timeout: int = 15, loop: Optional[asyncio.AbstractEventLoop] = None) -> Dict[str, Any]:
        loop = loop or asyncio.get_event_loop()
        
        info: Dict[str, Any] = await cls.wait_for_extraction(loop, yt_info_extractor, url=url, download=False, timeout=timeout)
        
        return info