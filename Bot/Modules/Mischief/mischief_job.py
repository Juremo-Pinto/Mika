import random

from discord import Guild
from Modules.Logging.logger import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class MischiefJob:
    def __init__(self, parent, guild: Guild):
        self.parent = parent
        
        assert isinstance(parent.scheduler, AsyncIOScheduler)
        self.job = parent.scheduler.add_job(self.mischief_interface, 'interval', seconds = parent.interval)
        self.guild = guild
        
        logger.debug(f"Mischief Job Loaded: {self.guild.name}")
    
    
    def mischief_interface(self):
        try:
            rdn = random.uniform(0, 100)
            logger.debug(f"{self.guild.name} Mischief: rdn at {rdn}")
            if rdn <= self.parent.settings["chance_percentage"]:
                self.parent.bot.loop.create_task(
                    self.execute_trolling()
                    )
        except Exception as e:
            self.parent.run_error(e)
    
    
    async def execute_trolling(self):
        self.job.pause()
        await self.parent.perform_a_minuscule_amount_of_despicable_actions(self.guild)
        self.job.resume()