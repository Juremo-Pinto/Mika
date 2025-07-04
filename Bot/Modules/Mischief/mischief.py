# mischief.py

import json
from Modules.reloadable import ReloadableComponent
from Modules.Mischief.mischief_job import MischiefJob
from Modules.settings import Settings
from Modules.Logging.logger import logger
import os, random, discord, asyncio, resources_path
from typing import Dict, List

from discord.ext.commands import Bot

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from Modules.utils import Utils
from Modules.information_manager import InformationManager


REGULAR_AUDIO_PATH: str = os.path.join(resources_path.AUDIOS, "Regular")
RARE_AUDIO_PATH: str = os.path.join(resources_path.AUDIOS, "Rare")
JSON_CHANCE_PATH: str = os.path.join(RARE_AUDIO_PATH, "rare_chances.json")


class Mischief(ReloadableComponent):
    """A considerably small amount of mischief will be caused.
    """
    def __init__(self, bot: Bot):
        super().__init__()
        
        self.bot = bot
        self.info_manager = InformationManager(self.bot)
        
        self.settings = Settings("mischief")
        self.settings.setup(
                guilds = [
                        "Whatsapp 2",
                        "Bot Testing Ground",
                        "VILA DO CHAVES",
                    ],
                chance_percentage = 1,
                interval_seconds = 10
            }
        
        
        self.mischief_job_registry: List[MischiefJob] = []
        self.scheduler = AsyncIOScheduler()
    
    
    def reload(self):
        self.bot.loop.create_task(self.setup())
    
    
    async def commence_moderate_mischief(self):
        """STARTS THE FUN
        """
        logger.info('Mischief: Initialized the funny lmao xdxd')
        await self.setup()
        
        self.scheduler.start()
    
    
    async def setup(self):
        self.mischief_job_registry.clear()
        self.scheduler.remove_all_jobs()
        
        self.interval: int = self.settings["interval_seconds"]
        
        for guild in self.settings["guilds"]:
            fetched_guild = await self.info_manager.fetch_guild_by_name(guild)
            
            if fetched_guild is not None:
                job_schedule = MischiefJob(self, fetched_guild)
                self.mischief_job_registry.append(job_schedule)
        
        self.regular_audios = os.listdir(REGULAR_AUDIO_PATH)
        self.rare_audios = [path for path in os.listdir(RARE_AUDIO_PATH) if not path.endswith(".json")]
        
        if not os.path.exists(JSON_CHANCE_PATH):
            Mischief.create_chance_json()
        
        await self.load_json()
        await self.fill_json_default_songs() 
    
    
    @staticmethod
    def create_chance_json():
        with open(JSON_CHANCE_PATH, 'x') as f:
            default_structure = {
                "rare_chance_percentage": 5,
                
                "default_generated_chance": 10,
                "individual_audio_chance": {
                } 
            }
            json.dump(default_structure, f, indent=4)
    
    
    async def QUIT_HAVING_FUN(self):
        """ends the fun D:"""
        self.scheduler.remove_all_jobs()
    
    
    def run_error(self, error: Exception):
        self.bot.loop.create_task(self._on_error(error=error))
    
    
    async def _on_error(self, error: Exception):
        if Utils.has_terminal():
            raise error
        
        dev = await self.info_manager.get_bot_dev()
        
        if dev:
            await dev.send(f'Error in MISCHIEF:\n{error}')
    
    
    async def get_populated_vcs(self, guild: discord.Guild) -> List[discord.VoiceChannel]:
        return [voice_channel for voice_channel in guild.voice_channels if len(voice_channel.voice_states) > 0]
    
    
    async def save_json(self):
        with open(JSON_CHANCE_PATH, 'w') as f:
            json.dump(self.chances, f, indent=4)
    
    
    async def load_json(self):
        with open(JSON_CHANCE_PATH, 'r') as f:
            self.chances = json.load(f)
    
    
    async def fill_json_default_songs(self):
        song_chances: Dict[str, int] = self.chances["individual_audio_chance"]
        default_chance = self.chances["default_generated_chance"]
        
        for filename in self.rare_audios:
            song_chances.setdefault(filename, default_chance)
        
        self.chances["individual_audio_chance"] = song_chances
        await self.save_json()
    
    
    async def get_rare_audio(self):
        audio_rarity_weights: Dict[str, int] = self.chances["individual_audio_chance"]
        total_audio_weight = sum(audio_rarity_weights.values())
        
        selection_threshold = random.randrange(0, total_audio_weight)
        cumulative_weight = 0
        
        for filename in audio_rarity_weights:
            cumulative_weight += audio_rarity_weights[filename]
            
            if cumulative_weight >= selection_threshold:
                audio_path = os.path.join(RARE_AUDIO_PATH, filename)
                
                return audio_path, filename
    
    
    async def get_regular_audio(self):
        selected_audio: str = random.choice(self.regular_audios)
        audio_path: str = os.path.join(REGULAR_AUDIO_PATH, selected_audio)
        
        return audio_path, selected_audio
    
    
    async def get_random_audio(self):
        random_value = random.uniform(0, 100)
        logger.debug(f"Mischief: Random value for rare audio selection: {random_value}")
        if random_value < self.chances["rare_chance_percentage"]:
            audio_path, name = await self.get_rare_audio()
        else:
            audio_path, name = await self.get_regular_audio()
        
        return audio_path, name
    
    
    async def perform_a_minuscule_amount_of_despicable_actions(self, guild: discord.Guild):
        if guild.voice_client:
            logger.debug("Bot already in a voice channel")
            return
        
        active_voice_channels = await self.get_populated_vcs(guild)
        
        if len(active_voice_channels) == 0:
            logger.debug(f'Mischief: No voice channels available in {guild.name}')
            return
        
        await random.choice(active_voice_channels).connect()
        
        audio_path, audio_name = await self.get_random_audio()
        audio_source = discord.FFmpegPCMAudio(audio_path)
        
        voice_client: discord.VoiceClient = self.bot.voice_clients[0]
        
        await asyncio.sleep(random.randint(1, 10))
        
        playback_complete_event = asyncio.Event()
        
        def stop(err: Exception | None):
            if err:
                logger.error(err)
            playback_complete_event.set()
        
        voice_client.play(audio_source, after = stop)
        logger.info(f"Mischief: Love me some {audio_name}")
        
        await playback_complete_event.wait()
        
        await asyncio.sleep(random.uniform(0, 0.2))  
        await voice_client.disconnect()