import asyncio
from typing import List
import discord

from discord.ext import commands
from discord.ext.commands import Context, Bot

from Modules.Logging.logger import logger
from Modules.settings.per_user import UserSettings
from Modules.utils import StringTools

from Cogs.tts.abc import TTSEngineBase

# Temporary
from Cogs.tts.engines.google_tts import GoogleTTSEngine
from Cogs.tts.engines.sam_tts import SamTTSEngine


class TextToSpeech(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        
        self.user_settings = UserSettings("tts")
        self.user_settings.set_structure(
            lang = 'es',
            engine = 'google'
        )
        
        self.engines = { # TODO: make this auto/modular instead of fixed dict (detect from tts/engines)
            'sam': SamTTSEngine,
            'google': GoogleTTSEngine
        }
        
        self.flag_dict = {}
        self.tts_queue: List[TTSEngineBase] = {}
    
    async def cog_load(self):
        logger.info(f"Cog Loaded: {self.__cog_name__}")
    
    def get_engine(self, engine_name) -> TTSEngineBase:
        return self.engines.get(engine_name)
    
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
        
        text = text.removeprefix(pref).removeprefix(cmd).strip() # workaround lmffao
        
        
        await self.enqueue_tts(text, user_id, vc, ctx.guild.id)
    
    
    @commands.command(name="tts-engine")
    async def change_tts_engine(self, ctx: Context, engine):
        if engine not in self.engines.keys():
            await ctx.reply("fake engine")
            return
        
        user_id = ctx.author.id
        engine_class = self.get_engine(engine)
        
        self.user_settings.set_for_user(user_id, "engine", engine)
        self.user_settings.set_for_user(user_id, "lang", engine_class.def_lang)
        
        ctx.send(f"i am now {engine}")
    
    async def try_send_dict(self, destination, dict: dict):
        message = "Language name - Language Code (the one youll use in the command)\n\n"
        
        for key, value in dict.items():
            message += f"{value} - {key}\n"
        
        await destination.send(message)
    
    @commands.command(name="lang", aliases=['language'])
    async def set_lang(self, ctx, lang = None, *, extra_args = None): # TODO: Implement extra args storage for special lang codes (eg: SamTTSEngine's "custom" language)
        user = ctx.author
        
        user_engine = self.user_settings.get_for_user(user.id, "engine")
        engine = self.get_engine(user_engine)
        
        if lang is None or lang.lower() == "help":
            await self.try_send_dict(user, engine.get_languages())
            return
        
        if not engine.language_exists(lang):
            await ctx.send("fake language")
            return
        
        self.user_settings.set_for_user(user.id, 'lang', lang)
        
        await ctx.send(f'ok u {lang} now')
    
    
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
            except:
                logger.warning("TTS: bot encountered error, skipping")
        
        if guild_id in self.tts_queue.keys():
            del self.tts_queue[guild_id]
    
    
    async def tts_speak(self, tts: TTSEngineBase, vc):
        audio_source = await tts.get_audio_source()
        
        flag = asyncio.Event()
        
        if vc:
            vc.play(audio_source, after= lambda e: flag.set())
            await flag.wait()
    
    
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
    
    
    async def get_voice_client(self, text):
        ctx = await self.bot.get_context(text)
        return ctx.voice_client
    
    
    async def get_gtts_object(self, user_id, text):
        user_lang = self.user_settings.get_for_user(user_id, 'lang')
        user_engine = self.user_settings.get_for_user(user_id, 'engine')
        
        engine = self.get_engine(user_engine)
        
        return engine(text=text, lang=user_lang)
    
    
    async def enqueue_tts(self, text, user_id, vc, guild_id):
        text = StringTools.normalize_str(text)
        
        queue_exists = guild_id in self.tts_queue.keys()
        
        self.tts_queue.setdefault(guild_id, [])
        
        tts = await self.get_gtts_object(user_id, text)
        
        self.tts_queue[guild_id].append(tts)
        
        if not queue_exists:
            await self.tts_loop(vc, guild_id)
    
    
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