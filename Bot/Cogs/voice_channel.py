import asyncio, discord

from discord.ext import commands
from Modules.command_manipulation.command_extension import command_extension
from Modules.command_permissions import role_blacklisted
from Modules.Logging.logger import logger

class VoiceChatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ping_list = set()
    
    
    async def cog_load(self):
        logger.info(f"Cog Loaded: {self.__cog_name__}")
    
    
    @commands.command("joinCall", aliases = ["entra"])
    @command_extension("ai", "ae")
    @role_blacklisted("forbid_audio_playback", "forbid_voice_chat_control",
        rejection_message="Tu tá BANIDO de mandar o bot coisar na call")
    async def joinCall(self, ctx):
        if hasattr(ctx.author.voice, 'channel'):
            await ctx.reply("ok <:cat:1264072257433632789>")
            await ctx.author.voice.channel.connect()
        else:
            await ctx.reply("Tenta entrar na call primeiro")
    
    
    @commands.command("leaveCall", aliases = ["vaza", "sai"])
    @role_blacklisted("forbid_audio_playback", "forbid_voice_chat_control",
        rejection_message="Tu tá BANIDO de mandar o bot coisar na call")
    async def leaveCall(self, ctx):
        current_call = ctx.voice_client
        
        if current_call:
            await current_call.disconnect()
            await ctx.reply("ok <:cat:1264072257433632789>")
        else:
            await ctx.reply("eu nem to em call uai")
    
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member != self.bot.user:
            return
        
        if before.channel and not after.channel:
            self.ping_list.remove(before.channel.id)
            logger.info(f'Bot has been disconnected from "{before.channel.name}", in "{before.channel.guild.name}"')
        
        elif not before.channel and after.channel:
            await self.new_connection(after.channel.guild.voice_client, after.channel.id)
            logger.info(f'Bot has joined the "{after.channel.name}" voice channel, in {after.channel.guild.name}')
        
        elif before.channel and after.channel and before.channel != after.channel:
            self.ping_list.remove(before.channel.id)
            await self.new_connection(after.channel.guild.voice_client, after.channel.id)
            logger.info(f'Bot has moved from "{before.channel.name}" to "{after.channel.name}", in {after.channel.guild.name}')
    
    
    async def new_connection(self, voice_client, channel_id):
        self.ping_list.add(channel_id)
        self.bot.loop.create_task(self.keep_connection_alive(voice_client))
    
    
    async def keep_connection_alive(self, voice_client):
        while voice_client.channel.id in self.ping_list:
            try:
                await voice_client.channel.guild.me.edit(nick="Tato")
                logger.debug(f"Ping! in '{voice_client.channel.guild.name}'")
            except discord.ClientException:
                pass
            await asyncio.sleep(15)




async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceChatCommands(bot))