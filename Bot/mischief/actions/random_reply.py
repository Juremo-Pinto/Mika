import random
from Modules.Logging.logger import logger
from Modules.settings.settings import Settings
from mischief.interface import TextMischief

from discord.ext.commands import Context, Bot


class RandomReplyMischief(TextMischief):
    mischief_name = "Random Reply"
    mischief_description = "Has a chance to just fucking reply to you message bruuuuuhhhhh"
    
    def __init__(self, bot: Bot):
        self.bot = bot
        
        self.settings = Settings("random_reply", section="mischief")
        self.settings.setup(
                min_amount = 500,
                max_amount = 5000,
                
                possible_texts = [
                    "Diza",
                    "Generally agreeable opinion",
                    "I agree, --PING--",
                    "I agree, DUMBASS"
                ]
            )
        
        self.index = 0
        self.randomize_index()
    
    def randomize_index(self):
        self.index = random.randrange(
            start=self.settings['min_amount'],
            stop=self.settings['max_amount'] + 1
        )
    
    async def check(self, normalized_text, message):
        if self.index <= 0:
            self.randomize_index()
            return True
        
        self.index -= 1
        logger.debug(f"RandomReplyMischief: Index = {self.index}")
        return False
    
    def reload(self):
        self.randomize_index()
    
    def format(self, text, ctx: Context):
        author_mention = ctx.author.mention
        text = text.replace("--PING--", f"{author_mention}")
        
        logger.debug(text)
        
        return text
    
    def get_text(self):
        all_text = self.settings["possible_texts"]
        selected_text = random.choice(all_text)
        return selected_text
    
    async def execute(self, normalized_text, message):
        ctx = await self.bot.get_context(message)
        
        text = self.get_text()
        text = self.format(text, ctx)
        
        await ctx.reply(text)