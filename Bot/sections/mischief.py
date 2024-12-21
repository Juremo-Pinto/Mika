# mischief.py

import random
import nextcord
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from Bot.information_manager import information_manager

class mischief:
    """A considerably small amount of mischief will be caused.
    """
    def __init__(self, bot: nextcord.Client, loop, *, servers_with_tomfoolery_present: list[str], playable_audio_list: list[str], chance_denominator: int = 100):
        self.bot = bot
        self.loop = loop
        self.utilities = information_manager(self.bot)
        
        self.servers_with_tomfoolery_present = servers_with_tomfoolery_present
        self.playable_audio_list = playable_audio_list
        self.chance_denominator = chance_denominator
        
        self.schedulerJobDict = {}
        self.scheduler = AsyncIOScheduler()




    async def commence_moderate_mischief(self):
        """STARTS THE FUN
        """
        print('it starts')

        self.schedulerJobDict['theTrollingJob'] = self.scheduler.add_job(self.mischief_interface, 'interval', seconds = 10)
        self.scheduler.start()



    async def mischief_interface(self):
        zap2 = await self.utilities.fetch_server_by_name('Whatsapp 2')

        if not any(VcClients.guild.id == zap2.id for VcClients in self.bot.voice_clients):
            if random.randint(1, self.chance_denominator) == 1:
                print('time to perform some tomfoolery')
                
                await self.performAMinusculeAmountOfDespicableActions()
            else:
                print('nah')
        
        else:
            print('unfortunately it is already here')



    async def getPopulatedVc(self):
        voice_channels = []
        
        for server in self.servers_with_tomfoolery_present:
            adquired_server = await self.utilities.fetch_server_by_name(server)
            voice_channels += adquired_server.voice_channels

        print('adquiring populated Vcs')

        return [voice_channel for voice_channel in voice_channels if len(voice_channel.voice_states) > 0]



    async def performAMinusculeAmountOfDespicableActions(self):
        print('doing a little trolling')

        voice_channels = await self.getPopulatedVc()

        if len(voice_channels) == 0:
            print('unable to perform the little trolling')
            return
        
        await random.choice(voice_channels).connect()

        selected_audio = random.choice(self.playable_audio_list)
        source = nextcord.FFmpegPCMAudio(f"Audios/{selected_audio}")
        vc_bot_client = self.bot.voice_clients[0]

        await asyncio.sleep(random.randint(1, 10))

        async def stop(err):
            if err:
                print(err)
            await asyncio.sleep(random.uniform(0, 0.6))  
            await vc_bot_client.disconnect() 
            print('enderd the little trolling')

        vc_bot_client.play(source, after = stop)