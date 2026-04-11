import random
from modules.logging.logger import logger
from modules.settings.settings import Settings
from mischief.interface import TextMischief

from discord.ext.commands import Context, Bot
from discord import Message

class parentsTag(TextMischief):
    mischief_name = "Respond to Parents"
    mischief_description = "Always replies to Fred and Charlie when mentioned through @"
    
    def __init__(self, bot: Bot):
        self.bot = bot
        
        self.settings = Settings("tag_response", section="mischief")
        self.settings.setup(
                
                possible_texts = [
                    "Haaiiii :D",
                    "Hello father figure.",
                    "--PING--",
                    "HI DAD!",
                    "Whats up?"
                ]
            )
    
    async def check(self, normalized_text, message: Message):
        
        if message.author.id == 629675130028818444 or message.author.id == 508268780586139648:
        
            if "<@1491896981868515399>" in normalized_text:
                return True
        
    
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