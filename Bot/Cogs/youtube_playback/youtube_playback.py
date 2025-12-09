import asyncio, os, random, yt_dlp, resources_path

from typing import Dict, List

from discord import Member, VoiceClient
from discord.ext import commands
from discord.ext.commands import Bot, Context
from unidecode import unidecode

from Modules.Logging.logger import logger
from Modules.command_manipulation.command_extension import command_extension
from Modules.cache import JsonCache
from Cogs.youtube_playback.YTDLSource import YTDLSource
from Cogs.youtube_playback.YTUtils import *
from Modules.command_permissions import role_blacklisted

class youtube_playback(commands.Cog):
    def __init__(self, bot: Bot):
        self._bot = bot
        
        self._music_queue: Dict[int, List[str]] = {}
        self._current_music: Dict[int, str] = {}
        
        cache_file_path = os.path.join(resources_path.CACHE, 'yt-playback_info_cache.json')
        self._info_cache = JsonCache(cache_file_path, size_limit=50000)
    
    async def cog_load(self):
        logger.info(f"Cog Loaded: {self.__cog_name__}")
    
    async def _initialize_dicts(self, ctx: Context):
        voice_channel_id = await get_voice_channel_id(ctx.voice_client)
        
        self._music_queue.setdefault(voice_channel_id, [])
        self._current_music.setdefault(voice_channel_id, None)
    
    async def _is_playback_new(self, voice_client: VoiceClient):
        channel_id = await get_voice_channel_id(voice_client)
        
        return not voice_client.is_playing() and self._current_music[channel_id] is None
    
    async def _get_info_and_cache(self, url: str):
        info = await YTDLSource.get_info_from_url(url)
        self._info_cache.modify(url, await clean_info(info=info))
        return info
    
    async def _song_info_retriever(self, ctx: Context, url: str, cache: bool = True):
        try:
            if cache:
                return self._info_cache.get(url, bump_to_top=True) or await self._get_info_and_cache(url)
            return await YTDLSource.get_info_from_url(url)
            
        except yt_dlp.DownloadError:
            await ctx.reply("Isso literalmente não existe")
            await ctx.message.delete()
        except asyncio.TimeoutError:
            await ctx.send("ih deu merda fi")
            await ctx.message.delete()
        
        return None
    
    
    @commands.command("play", aliases = ["toca"])
    @role_blacklisted('forbid_audio_playback', 'forbid_youtube_playback', rejection_message= "Tu tá BANIDO de musicar")
    async def extract_command_parameters(self, ctx: Context, *, query: str):
        voice_client = ctx.voice_client
        if not voice_client:
            await ctx.reply("Não to em nenhuma call cabeçudo")
            await ctx.author.send('"aproveita e entra ai" é o comando pra entrar em call')
            return
        
        command_list = query.split()
        
        is_shuffle = await is_shuffle(command_list) if len(command_list) > 1 else False
        url = command_list[0]
        
        await ctx.reply("Belezura, calma ae")
        await self._handle_request(ctx, url, is_shuffle)
    
    
    async def _handle_request(self, ctx: Context, url: str, is_shuffle: bool):
        await self._initialize_dicts(ctx)
        
        if await is_playlist(url):
            await self._handle_playlist(ctx, url, is_shuffle)
        else:
            await self._handle_individual(ctx, url)
    
    
    async def _handle_playlist(self, ctx: Context, url: str, is_shuffle: bool):
        playlist_info = await self._song_info_retriever(ctx, url, cache=False)
        await ctx.message.delete()
        
        if playlist_info is None:
            return
        
        song_list = playlist_info['entries']
        voice_channel_id = await get_voice_channel_id(ctx.voice_client)
        
        for song in song_list:
            if not self._info_cache.has(song['url']):
                self._info_cache.modify(song['url'], song)
        self._info_cache.reset_keys()
        
        if is_shuffle:
            await ctx.send("embaraiado ainda ó")
            random.shuffle(song_list)
        
        self._music_queue[voice_channel_id] += song_list
        
        if await self._is_playback_new(ctx.voice_client):
            self._bot.loop.create_task(self._main_playback_loop(ctx))
        else:
            await ctx.send('Botado na fila (a playlist inteira)')
    
    
    
    async def _handle_individual(self, ctx: Context, url: str):
        filtered_url = await remove_url_parameters(url)
        song_info = await self._song_info_retriever(ctx, filtered_url)
        
        if song_info is None:
            return
        
        song_info['url'] = filtered_url
        await ctx.message.delete()
        
        voice_channel_id = await get_voice_channel_id(ctx.voice_client)
        
        if await self._is_playback_new(ctx.voice_client):
            self._current_music[voice_channel_id] = song_info
            self._bot.loop.create_task(self._main_playback_loop(ctx))
        else:
            self._music_queue[voice_channel_id] += [song_info]
            await ctx.send('Botado na fila')
    
    
    
    async def _main_playback_loop(self, ctx: Context):
        voice_channel_id = await get_voice_channel_id(ctx.voice_client)
        
        current_song = self._current_music.get(voice_channel_id)
        if current_song is not None:
            await self._play_song(ctx, current_song)
        
        while len(self._music_queue[voice_channel_id]) > 0:
            self._current_music[voice_channel_id] = self._music_queue[voice_channel_id].pop(0)
            await self._play_song(ctx, self._current_music[voice_channel_id])
        
        self._current_music[voice_channel_id] = None
        await ctx.send("Cabo a fila")
    
    
    
    async def _play_song(self, ctx: Context, url: str):
        try:          
            async with ctx.typing():
                playable_song_object = await YTDLSource.stream_from_url(url['url'], loop= self._bot.loop)
            
            if not ctx.voice_client:
                return
            
            finished = asyncio.Event()
            
            ctx.voice_client.play(playable_song_object, after= lambda e: finished.set())
            
            await ctx.send(f"Tocando: **{url['title']}**")
            await finished.wait()
        
        except (yt_dlp.utils.DownloadError, asyncio.TimeoutError):
            await ctx.send("Deu ruim, proxima música")
    
    
    
    @commands.command("skip", aliases = ["skipa", "pula"])
    @role_blacklisted('forbid_audio_playback', 'forbid_youtube_playback', rejection_message= "Tu tá BANIDO de musicar")
    async def skip(self, ctx: Context, amount: str | None = None):
        voice_client = ctx.voice_client
        voice_channel_id = await get_voice_channel_id(voice_client)
        
        if amount is None or not isinstance(amount, (int, str)) or (isinstance(amount, int) and amount <= 0):
            amount = 1
        
        if voice_client:
            await self._initialize_dicts(ctx)
            
            if isinstance(amount, str) and amount.strip().lower() in ['tudo', 'all', 'todos', 'todes']:
                await self._skip_all(ctx, voice_channel_id)
            elif amount > 1 and len(self._music_queue[voice_channel_id]) >= amount:
                del self._music_queue[voice_channel_id][:amount - 1]
                await ctx.reply("tá")
            elif amount > 1:
                await ctx.send("Como que skipa um numero maior que a fila porra")
                await ctx.send(f"(Nota: a fila tem {len(self._music_queue[voice_channel_id]) + 1} musicas)")
                return
            
            voice_client.stop()
        else:
            await ctx.reply("Oque, porra")
    
    async def _skip_all(self, ctx: Context, channel_id: int):
            self._music_queue[channel_id] = []
            self._current_music[channel_id] = None
            await ctx.reply("Oloco tabão")
    
    
    @commands.command(name='limpa', aliases = ['clean', 'limpar', 'esvazia'])
    @command_extension('a fila', 'as musica')
    @role_blacklisted('forbid_audio_playback', 'forbid_youtube_playback', rejection_message= "Tu tá BANIDO de musicar")
    async def clear_queue(self, ctx: Context):
        channel_id = await get_voice_channel_id(ctx.voice_client)
        
        if not channel_id:
            await ctx.reply('Oque, porra')
            return
        
        self._music_queue[channel_id] = []
        await ctx.send('ok')
    
    
    @commands.command("playing", aliases = ["diz"])
    async def playing(self, ctx: Context, *, msg: str):
        voice_channel_id = await get_voice_channel_id(ctx.voice_client)
        
        if voice_channel_id is not None:
            await self._initialize_dicts(ctx)
        
        if unidecode(msg.strip().lower()) in ["oq ta tocando", "oq ta tocano", "a musica que esta sendo reproduzida nesse momento", "a musica", "essa musica"]:
            if voice_channel_id and self._current_music[voice_channel_id]:
                await ctx.reply(f"**{self._current_music[voice_channel_id]['title']}**")
            else:
                await ctx.reply("nada")
        
        elif unidecode(msg.strip().lower()) in ["as musica", "todas as musica", "tudo", "a fila", "a lista"]:
            if voice_channel_id and len(self._music_queue[voice_channel_id]) > 0 and self._music_queue[voice_channel_id][0]:
                await self._compile_messages(ctx, voice_channel_id)
            elif voice_channel_id and self._current_music[voice_channel_id] is not None:
                await ctx.send(f"1 - **{self._current_music[voice_channel_id]['title']}**")
            else:
                await ctx.reply("a fila ta vazia fi")
    
    
    async def _compile_messages(self, ctx: Context, voice_channel_id: int):
        message = f"1 - **{self._current_music[voice_channel_id]['title']}**\n"
        
        song_placement = 2
        
        for song in self._music_queue[voice_channel_id]:
            song_message = f"{song_placement} - {song['title']}\n"
            
            if song_placement > 100:
                message += f"*+ {(len(self._music_queue[voice_channel_id]) - song_placement) + 2} outras...*"
                break
            
            if len(message) + len(song_message) > 2000:
                await ctx.send(message)
                message = song_message
            else:
                message += song_message
            
            song_placement += 1
        
        await ctx.send(message)
    
    
    @commands.command("shuffle", aliases = ["embaralha", "embaraia"])
    @role_blacklisted(
        'forbid_audio_playback', 'forbid_youtube_playback',
        rejection_message= "Tu tá BANIDO de musicar")
    async def shuffle_list(self, ctx: Context):
        voice_channel_id = await get_voice_channel_id(ctx.voice_client)
        
        if voice_channel_id in self._music_queue and len(self._music_queue[voice_channel_id]) > 0:
            random.shuffle(self._music_queue[voice_channel_id])
            await ctx.reply("Ok tá bem aleatório")
        
        else:
            await ctx.send("que?")
    
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceClient | None, after: VoiceClient | None):
        if member == self._bot.user and before.channel and not after.channel:
            self._music_queue[before.channel.id] = []
            self._current_music[before.channel.id] = None


async def setup(bot: Bot):
    await bot.add_cog(youtube_playback(bot))