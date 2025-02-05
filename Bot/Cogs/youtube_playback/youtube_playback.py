import asyncio
import os
import random

from nextcord.ext import commands
from unidecode import unidecode

import yt_dlp

from Modules.command_utils import command_extension
from resources_path import resources_path
from Modules.cache import JsonCache
from Cogs.youtube_playback.YTDLSource import YTDLSource
from Modules.command_permissions import role_blacklisted

class youtube_playback(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.music_queue = {}
        self.current_music = {}
        
        cache_file_path = os.path.join(resources_path('cache'), 'yt-playback_info_cache.json')
        self.info_cache = JsonCache(cache_file_path, size_limit=50000)
    
    async def get_voice_channel_id(self, voice_client):
        return voice_client.channel.id if voice_client else None
    
    async def is_shuffle(self, command_list):
        return any(keyword in command_list[i].lower() for i in range(0, len(command_list)) for keyword in ["aleatorio", "shuffle", "embaralha", "embaraia", "embaralhado", "embaraiado"])
    
    async def is_playlist(self, url):
        root_url = url.split('?')[0]
        return root_url == "https://www.youtube.com/playlist"
    
    async def remove_url_parameters(self, full_url):
        return full_url.split('&')[0]
    
    async def initialize_dicts(self, ctx):
        voice_channel_id = await self.get_voice_channel_id(ctx.voice_client)
        
        self.music_queue.setdefault(voice_channel_id, [])
        self.current_music.setdefault(voice_channel_id, None)
    
    async def is_playback_new(self, voice_client):
        channel_id = await self.get_voice_channel_id(voice_client)
        
        return not voice_client.is_playing() and self.current_music[channel_id] is None
    
    async def _info_clean(self, info):
        unwanted_keys = ["formats", "thumbnails", "thumbnail", "automatic_captions", "heatmap", "requested_formats", "subtitles", "description"]
        
        for key in unwanted_keys:
            if key in info:
                del info[key]
        
        return info
    
    async def get_info_and_cache(self, url):
        info = await YTDLSource.get_info_from_url(url)
        self.info_cache.modify(url, await self._info_clean(info=info))
        return info
    
    
    async def song_info_retriever(self, ctx, url, cache=True):
        try:
            if cache:
                return self.info_cache.get(url, bump_to_top=True) or await self.get_info_and_cache(url)
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
    async def extract_command_parameters(self, ctx, *, query):
        command_list = query.split()
        voice_client = ctx.voice_client
        
        is_shuffle = await self.is_shuffle(command_list) if len(command_list) > 1 else False
        url = command_list[0]
        
        if voice_client:
            await ctx.reply("Belezura, calma ae")
            await self.handle_request(ctx, url, is_shuffle)
        else:
            await ctx.reply("Não to em nenhuma call cabeçudo")
            await ctx.author.send('"aproveita e entra ai" é o comando pra entrar em call')
    
    
    async def handle_request(self, ctx, url, is_shuffle):
        await self.initialize_dicts(ctx)
        
        if await self.is_playlist(url):
            await self.handle_playlist(ctx, url, is_shuffle)
        else:
            await self.handle_individual(ctx, url)
    
    
    async def handle_playlist(self, ctx, url, is_shuffle):
        playlist_info = await self.song_info_retriever(ctx, url, cache=False)
        await ctx.message.delete()
        
        if playlist_info is None:
            return
        
        song_list = playlist_info['entries']
        voice_channel_id = await self.get_voice_channel_id(ctx.voice_client)
        
        for song in song_list:
            if not self.info_cache.has(song['url']):
                self.info_cache.modify(song['url'], song)
        self.info_cache.reset_keys()
        
        if is_shuffle:
            await ctx.send("embaraiado ainda ó")
            random.shuffle(song_list)
        
        self.music_queue[voice_channel_id] += song_list
        
        if await self.is_playback_new(ctx.voice_client):
            self.bot.loop.create_task(self.main_playback_loop(ctx))
        else:
            await ctx.send('Botado na fila (a playlist inteira)')
    
    
    
    async def handle_individual(self, ctx, url):
        filtered_url = await self.remove_url_parameters(url)
        song_info = await self.song_info_retriever(ctx, filtered_url)
        
        if song_info is None:
            return
        
        song_info['url'] = filtered_url
        await ctx.message.delete()
        
        voice_channel_id = await self.get_voice_channel_id(ctx.voice_client)
        
        if await self.is_playback_new(ctx.voice_client):
            self.current_music[voice_channel_id] = song_info
            self.bot.loop.create_task(self.main_playback_loop(ctx))
        else:
            self.music_queue[voice_channel_id] += [song_info]
            await ctx.send('Botado na fila')
    
    
    
    async def main_playback_loop(self, ctx):
        voice_channel_id = await self.get_voice_channel_id(ctx.voice_client)
        
        current_song = self.current_music.get(voice_channel_id)
        if current_song is not None:
            await self.play_song(ctx, current_song)
        
        while len(self.music_queue[voice_channel_id]) > 0:
            self.current_music[voice_channel_id] = self.music_queue[voice_channel_id].pop(0)
            await self.play_song(ctx, self.current_music[voice_channel_id])
        
        self.current_music[voice_channel_id] = None
        await ctx.send("Cabo a fila")
    
    
    
    async def play_song(self, ctx, current_song):
        try:          
            async with ctx.typing():
                playable_song_object = await YTDLSource.stream_from_url(current_song['url'], loop= self.bot.loop)
            
            if not ctx.voice_client:
                return
            
            finished = asyncio.Event()
            
            ctx.voice_client.play(playable_song_object, after= lambda e: finished.set())
            await ctx.send(f"Tocando: **{current_song['title']}**")
            
            await finished.wait()
            
            print("Teste")
        
        except (yt_dlp.utils.DownloadError, asyncio.TimeoutError) as e:
                await ctx.send("Deu ruim, proxima música")
    
    
    
    @commands.command("skip", aliases = ["skipa", "pula"])
    @role_blacklisted('forbid_audio_playback', 'forbid_youtube_playback', rejection_message= "Tu tá BANIDO de musicar")
    async def skip(self, ctx, amount = None):
        voice_client = ctx.voice_client
        voice_channel_id = await self.get_voice_channel_id(voice_client)
        
        if amount is None or not isinstance(amount, (int, str)) or (isinstance(amount, int) and amount <= 0):
            amount = 1
        
        if voice_client:
            await self.initialize_dicts(ctx)
            
            if isinstance(amount, str) and amount.strip().lower() in ['tudo', 'all', 'todos', 'todes']:
                await self.skip_all(ctx, voice_channel_id)
            elif amount > 1 and len(self.music_queue[voice_channel_id]) >= amount:
                del self.music_queue[voice_channel_id][:amount - 1]
                await ctx.reply("tá")
            elif amount > 1:
                await ctx.send("Como que skipa um numero maior que a fila porra")
                await ctx.send(f"(Nota: a fila tem {len(self.music_queue[voice_channel_id]) + 1} musicas)")
                return
            
            voice_client.stop()
        else:
            await ctx.reply("Oque, porra")
    
    async def skip_all(self, ctx, channel):
            self.music_queue[channel] = []
            self.current_music[channel] = None
            await ctx.reply("Carai tudin? tabão")
    
    
    @commands.command(name='limpa', aliases = ['clean', 'limpar', 'esvazia'])
    @command_extension('a fila', 'as musica')
    @role_blacklisted('forbid_audio_playback', 'forbid_youtube_playback', rejection_message= "Tu tá BANIDO de musicar")
    async def clear_queue(self, ctx):
        channel_id = await self.get_voice_channel_id(ctx.voice_client)
        
        if not channel_id:
            await ctx.reply('Oque, porra')
            return
        
        self.music_queue[channel_id] = []
        await ctx.send('ok')
    
    
    @commands.command("playing", aliases = ["diz", "fala"])
    async def playing(self, ctx, *, msg):
        voice_channel_id = await self.get_voice_channel_id(ctx.voice_client)
        
        if voice_channel_id is not None:
            await self.initialize_dicts(ctx)
        
        if unidecode(msg.strip().lower()) in ["oq ta tocando", "oq ta tocano", "a musica que esta sendo reproduzida nesse momento", "a musica", "essa musica"]:
            if voice_channel_id and self.current_music[voice_channel_id]:
                await ctx.reply(f"**{self.current_music[voice_channel_id]['title']}**")
            else:
                await ctx.reply("nada")
        
        elif unidecode(msg.strip().lower()) in ["as musica", "todas as musica", "tudo", "a fila", "a lista"]:
            if voice_channel_id and len(self.music_queue[voice_channel_id]) > 0 and self.music_queue[voice_channel_id][0]:
                await self.compile_messages(ctx, voice_channel_id)
            elif voice_channel_id and self.current_music[voice_channel_id] is not None:
                await ctx.send(f"1 - **{self.current_music[voice_channel_id]['title']}**")
            else:
                await ctx.reply("a fila ta vazia fi")
    
    
    async def compile_messages(self, ctx, voice_channel_id):
        message = f"1 - **{self.current_music[voice_channel_id]['title']}**\n"
        
        song_placement = 2
        
        for song in self.music_queue[voice_channel_id]:
            song_message = f"{song_placement} - {song['title']}\n"
            
            if song_placement > 100:
                message += f"*+ {(len(self.music_queue[voice_channel_id]) - song_placement) + 2} outras...*"
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
    async def shuffle_list(self, ctx):
        voice_channel_id = await self.get_voice_channel_id(ctx.voice_client)
        
        if voice_channel_id in self.music_queue and len(self.music_queue[voice_channel_id]) > 0:
            random.shuffle(self.music_queue[voice_channel_id])
            await ctx.reply("Ok tá bem aleatório")
        
        else:
            await ctx.send("que?")
    
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user and before.channel and not after.channel:
            self.music_queue[before.channel.id] = []
            self.current_music[before.channel.id] = None


def setup(bot):
    bot.add_cog(youtube_playback(bot))