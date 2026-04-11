import random
from modules.logging.logger import logger
from modules.settings.settings import Settings
from mischief.interface import TextMischief

from discord.ext.commands import Context, Bot
from discord import Message


class RandomReplyMischief(TextMischief):
    mischief_name = "Random Reply"
    mischief_description = "Has a chance to just fucking reply to you message bruuuuuhhhhh"
    
    def __init__(self, bot: Bot):
        self.bot = bot
        
        self.settings = Settings("random_reply", section="mischief")
        self.settings.setup(
                min_amount = 0,
                max_amount = 5000,
                
                possible_texts = [
                    "Bars",
                    "Wtf are you on abt",
                    "Sure?, --PING--",
                    "HATE, LET ME TELL YOU HOW MUCH I- \nnah jk lmao i luv you :D"
                ]
            )
        
        self.index = 0
        self.randomize_index()
    
    def randomize_index(self):
        self.index = random.randrange(
            start=self.settings['min_amount'],
            stop=self.settings['max_amount'] + 1
        )
    
    async def check(self, normalized_text, message: Message):
        if message.author.id == self.bot.user.id:
            return
        
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