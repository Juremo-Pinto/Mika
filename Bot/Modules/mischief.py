# mischief.py

import os, random, discord, asyncio
from typing import Any, Dict, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from Modules.utils import Utils
from Modules.information_manager import InformationManager
from resources_path import resources_path

class Mischief:
    """A considerably small amount of mischief will be caused.
    """
    def __init__(self, bot: discord.Client, *, servers_with_tomfoolery_present: list[str], chance_denominator: int = 100, interval_in_seconds: int = 10):
        self.bot = bot
        self.info = InformationManager(self.bot)
        
        self.servers_with_tomfoolery_present = servers_with_tomfoolery_present
        self.chance_denominator = chance_denominator
        self.interval = interval_in_seconds
        
        self.scheduler_jobs_dict = {}
        self.scheduler = AsyncIOScheduler()
    
    
    async def commence_moderate_mischief(self):
        """STARTS THE FUN
        """
        print('Mischief: Initialized the funny lmao xdxd')
        await self._setup()
        
        self.scheduler_jobs_dict['theTrollingJob'] = self.scheduler.add_job(self.mischief_interface, 'interval', seconds = self.interval)
        self.scheduler.start()
    
    
    async def _setup(self):
        servers: List[discord.Guild] = []
        
        for guild in self.servers_with_tomfoolery_present:
            found_server = await self.info.fetch_guild_by_name(guild)
            
            if found_server is not None:
                servers.append(found_server)
        
        self.guilds = servers
    
    
    async def QUIT_HAVING_FUN(self):
        """ends the fun D:"""
        print('it ends')
        
        self.scheduler.remove_all_jobs()
    
    
    async def mischief_interface(self):
        try:
            if random.randint(1, self.chance_denominator) == 1:
                await self.perform_a_minuscule_amount_of_despicable_actions()
        except Exception as e:
            await self.on_error(e)
    
    
    async def on_error(self, error: Exception):
        if Utils.has_terminal():
            raise error
        
        dev = await self.info.get_bot_dev()
        
        if dev:
            await dev.send(f'Error in MISCHIEF:\n{error}')
    
    
    async def get_populated_vcs(self):
        voice_channels = []
        
        for guild in self.guilds:
            if not any(VcClients.guild.id == guild.id for VcClients in self.bot.voice_clients):
                voice_channels += guild.voice_channels
        
        return [voice_channel for voice_channel in voice_channels if len(voice_channel.voice_states) > 0]
    
    
    async def get_random_audio(self):
        playable_audio_list = os.listdir(resources_path('audio'))
        selected_audio = random.choice(playable_audio_list)
        return os.path.join(resources_path('audio'), selected_audio), selected_audio
    
    
    async def perform_a_minuscule_amount_of_despicable_actions(self):
        voice_channels = await self.get_populated_vcs()
        
        if len(voice_channels) == 0:
            print('Mischief: No voice channels available')
            return
        
        await random.choice(voice_channels).connect()
        
        audio_path, audio_name = await self.get_random_audio()
        source = discord.FFmpegPCMAudio(audio_path)
        
        vc_bot_client = self.bot.voice_clients[0]
        
        await asyncio.sleep(random.randint(1, 10))
        
        flag = asyncio.Event()
        
        def stop(err):
            if err:
                print(err)
            flag.set()
        
        vc_bot_client.play(source, after = stop)
        print(f"Mischief: Love me some {audio_name}")
        
        await flag.wait()
        
        await asyncio.sleep(random.uniform(0, 0.2))  
        await vc_bot_client.disconnect()