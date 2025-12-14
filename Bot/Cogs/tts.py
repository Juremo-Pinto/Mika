import asyncio
import discord

from gtts import gTTS
from gtts.lang import tts_langs
from discord.ext import commands
from discord.ext.commands import Context, Bot
from discord.utils import escape_mentions
from io import BytesIO

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
        
        self.tts_queue = {}
    
    
    async def cog_load(self):
        logger.info(f"Cog Loaded: {self.__cog_name__}")
    
    
    def language_exists(self, lang_code: str) -> bool:
        available = tts_langs()
        return lang_code in available.keys()
    
    
    async def get_language(self, text, default):
        keyword_list = text.split(' ')
        
        for word in keyword_list:
            if word.startswith("--lang:"):
                lang = word.removeprefix('--lang:').strip()
                text = text.replace(word, "")
                return text, lang
        
        return text, default
    
    
    @commands.command(name="fala", aliases=["tts"])
    async def call_tts(self, ctx: Context):
        vc = ctx.voice_client
        user_id = ctx.author.id
        
        if not vc:
            await ctx.reply("nuh uh")
            return
        
        text = ctx.message.clean_content
        pref = ctx.prefix
        cmd = ctx.invoked_with
        
        text = text.removeprefix(pref).removeprefix(cmd).strip()
        
        await self.enqueue_tts(text, user_id, vc, ctx.guild.id)
    
    
    @commands.command(name="lingua", aliases=["lang"])
    async def set_lang(self, ctx, *, lang):
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
        
        await self.enqueue_tts(message.clean_content, user.id, vc, guild.id)
    
    
    async def get_voice_client(self, text):
        ctx = await self.bot.get_context(text)
        return ctx.voice_client
    
    
    def clean_text(self, text):
        return text.lower()
    
    
    async def get_gtts_object(self, user_id, text):
        user_lang = self.user_settings.get_for_user(user_id, 'lang')
        
        text, language = await self.get_language(text, user_lang)
        
        if not self.language_exists(language):
            language = user_lang
        
        return gTTS(text=text, lang=language, slow=False)
    
    
    async def enqueue_tts(self, text, user_id, vc, guild_id):
        text = self.clean_text(text)
        
        queue_exists = guild_id in self.tts_queue.keys()
        
        self.tts_queue.setdefault(guild_id, [])
        tts = await self.get_gtts_object(user_id, text)
        self.tts_queue[guild_id].append(tts)
        
        if not queue_exists:
            await self.tts_loop(vc, guild_id)
    
    
    async def tts_loop(self, vc, guild_id):
        while(
            guild_id in self.tts_queue.keys()
            and len(self.tts_queue[guild_id]) > 0
            ):
            
            tts = self.tts_queue[guild_id].pop(0)
            
            try:
                await self.tts_speak(tts, vc)
            except AssertionError:
                logger.info("TTS: bot tried to speak a textless message, continuing...")
                continue
        
        if guild_id in self.tts_queue.keys():
            del self.tts_queue[guild_id]
    
    
    async def tts_speak(self, tts, vc):
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer) 
        audio_buffer.seek(0)
        
        audio_source = discord.FFmpegPCMAudio(audio_buffer, pipe=True, before_options='-re')
        
        flag = asyncio.Event()
        
        if vc:
            vc.play(audio_source, after= lambda e: flag.set())
            await flag.wait()
    
    
    def clear(self, guild_id):
        if guild_id in self.flag_dict.keys():
            del self.flag_dict[guild_id]
        
        if guild_id in self.tts_queue.keys():
            del self.tts_queue[guild_id]
    
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        
        if member == self.bot.user and before.channel != after.channel:
            self.clear(guild.id)
            return
        
        if guild.id not in self.flag_dict.keys():
            return
        
        tts_user = self.flag_dict[guild.id].get("user_id")
        
        if member.id == tts_user and before.channel != after.channel:
            self.clear(guild.id)
            return



async def setup(bot):
    await bot.add_cog(TextToSpeech(bot))