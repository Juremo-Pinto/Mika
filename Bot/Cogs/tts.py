import asyncio
import discord

from gtts import gTTS
from gtts.lang import tts_langs
from discord.ext import commands
from discord.ext.commands import Context, Bot
from io import BytesIO

from Modules.database_manager import DatabaseManager
from Modules.command_permissions import moderator
from Modules.Logging.logger import logger
from Modules.settings.per_user import UserSettings


class TextToSpeech(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        
        self.user_settings = UserSettings("tts")
        self.user_settings.set_structure(
            lang = 'es'
        )
        
        self.flag_dict = {}
    
    
    async def cog_load(self):
        logger.info(f"Cog Loaded: {self.__cog_name__}")
    
    
    def language_exists(self, lang_code: str) -> bool:
        available = tts_langs()  # GET ALL THE [[SUPPORTED LANGUAGES]]
        return lang_code.lower() in available
    
    
    async def get_language(self, msg, default):
        keyword_list = msg.split(' ')
        
        for word in keyword_list:
            if word.startswith("--lang:"):
                lang = word.removeprefix('--lang:').strip()
                msg = msg.replace(word, "")
                return msg, lang
        
        return msg, default
    
    
    @commands.command(name="fala", aliases=["tts"])
    async def call_tts(self, ctx: Context, *, msg):
        vc = ctx.voice_client
        user_id = ctx.author.id
        
        if not vc:
            await ctx.reply("nuh uh")
            return
        
        await self.tts_speak(msg, user_id, vc)
    
    
    
    async def tts_speak(self, msg, user_id, vc):
        user_lang = self.user_settings.get_for_user(user_id, 'lang')
        
        msg, language = await self.get_language(msg, user_lang)
        
        if not self.language_exists(language):
            language = user_lang
        
        tts = gTTS(text=msg, lang=language, slow=False)
        
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer) 
        audio_buffer.seek(0)
        
        audio_source = discord.FFmpegPCMAudio(audio_buffer, pipe=True)
        vc.play(audio_source)
    
    
    @commands.command(name="lingua", aliases=["lang"])
    async def set_lang(self, ctx, lang):
        user_id = ctx.author.id
        
        if not self.language_exists(lang):
            await ctx.send("fake language")
            return
        
        self.user_settings.set_for_user(user_id, 'lang', lang)
        
        await ctx.send(f'ok u {lang} now')
    
    
    @commands.command(name="tts-flag", aliases=["tts_flag", "ttsflag", "ttsf"])
    async def tts_flag(self, ctx: Context):
        await ctx.message.delete()
        
        voice = ctx.author.voice
        vc = ctx.voice_client
        
        if voice is None or vc is None:
            await ctx.send('nuh uh')
            return
        
        if voice.channel.id != vc.channel.id:
            await ctx.send('wrong VCs lmfao')
            return
        
        self.flag_dict[ctx.guild.id] = {
            "user_id": ctx.author.id,
            "channel_id": ctx.channel.id
        }
    
    @commands.command(name="tts-unflag", aliases=["tts_unflag", "ttsunflag", "ttsuf"])
    async def tts_unflag(self, ctx: Context):
        await ctx.message.delete()
        
        key = ctx.guild.id
        
        if key in self.flag_dict.keys():
            if self.flag_dict[key].get("user_id") == ctx.author.id:
                del self.flag_dict[key]
                return await ctx.send("aye")
        
        await ctx.send("nuh uh")
    
    
    async def get_voice_client(self, msg):
        ctx = await self.bot.get_context(msg)
        return ctx.voice_client
    
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        guild = message.guild
        
        if guild.id not in self.flag_dict.keys():
            return
        
        user = message.author
        channel = message.channel
        
        user_id = self.flag_dict[guild.id].get('user_id')
        
        if user_id is None or user_id != user.id:
            return
        
        channel_id = self.flag_dict[guild.id].get('channel_id')
        
        if channel_id is None or channel_id != channel.id:
            return
        
        vc = await self.get_voice_client(message)
        
        await self.tts_speak(message.content, user.id, vc)
    
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print("dhgsdklfhgsdfkjl")
        
        guild = member.guild
        
        if guild.id not in self.flag_dict.keys():
            return
        
        if member == self.bot.user and before.channel != after.channel:
            del self.flag_dict[guild.id]
            return
        
        tts_user = self.flag_dict[guild.id].get("user_id")
        
        if member.id == tts_user and before.channel != after.channel:
            del self.flag_dict[guild.id]
            return



async def setup(bot):
    await bot.add_cog(TextToSpeech(bot))