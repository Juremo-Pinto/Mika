# mischief.py

import random
import nextcord
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from Modules.information_manager import InformationManager
from resources_path import ResourcesPath

class Mischief:
    """A considerably small amount of mischief will be caused.
    """
    def __init__(self, bot: nextcord.Client, *, servers_with_tomfoolery_present: list[str], playable_audio_list_path: list[str], chance_denominator: int = 100):
        self.bot = bot
        self.info_manager = InformationManager(self.bot)
        
        self.servers_with_tomfoolery_present = servers_with_tomfoolery_present
        self.playable_audio_list = playable_audio_list_path
        self.chance_denominator = chance_denominator
        
        self.scheduler_jobs_dict = {}
        self.scheduler = AsyncIOScheduler()
        self.resources = ResourcesPath()


    async def commence_moderate_mischief(self):
        """STARTS THE FUN
        """
        print('it starts')
        
        self.scheduler_jobs_dict['theTrollingJob'] = self.scheduler.add_job(self.mischief_interface, 'interval', seconds = 10)
        self.scheduler.start()


    async def mischief_interface(self):
        if random.randint(1, self.chance_denominator) == 1:
            print('time to perform some tomfoolery')
            
            await self.perform_a_minuscule_amount_of_despicable_actions()
        
        # decided to omit the print stating it didnt happen because it would pollute the output way too much


    async def get_populated_vcs(self):
        voice_channels = []
        
        for server in self.servers_with_tomfoolery_present:
            adquired_server = await self.info_manager.fetch_guild_by_name(server)
            
            if not any(VcClients.guild.id == adquired_server.id for VcClients in self.bot.voice_clients):
                voice_channels += adquired_server.voice_channels
        
        print('adquiring populated Vcs')
        
        return [voice_channel for voice_channel in voice_channels if len(voice_channel.voice_states) > 0]


    async def perform_a_minuscule_amount_of_despicable_actions(self):
        print('doing a little trolling')
        
        voice_channels = await self.get_populated_vcs()
        
        if len(voice_channels) == 0:
            print('unable to perform the little trolling')
            return
        
        await random.choice(voice_channels).connect()
        
        selected_audio = random.choice(self.playable_audio_list)
        source = nextcord.FFmpegPCMAudio(f"{self.resources('audio')}/{selected_audio}")
        vc_bot_client = self.bot.voice_clients[0]
        
        await asyncio.sleep(random.randint(1, 10))
        
        async def stop(err):
            if err:
                print(err)
            await asyncio.sleep(random.uniform(0, 0.6))  
            await vc_bot_client.disconnect() 
            print('enderd the little trolling')
        
        vc_bot_client.play(source, after = stop)