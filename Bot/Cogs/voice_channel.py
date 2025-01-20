import asyncio
import nextcord
from nextcord.ext import commands

class VoiceChatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ping_list = []
    
    @commands.command("joinCall", aliases = ["entra"])
    async def joinCall(self, ctx, a1):
        if a1 in ["ai", "ae"]:
            if hasattr(ctx.author.voice, 'channel'):
                await ctx.reply("ok <:cat:1264072257433632789>")
                await ctx.author.voice.channel.connect()
                asyncio.run_coroutine_threadsafe(self.keep_connection_alive(ctx.voice_client), self.bot.loop)
                print(f'Bot has joined the "{ctx.author.voice.channel.name}" voice channel, in')
            else:
                await ctx.reply("Tenta entrar na call primeiro")
    
    
    @commands.command("leaveCall", aliases = ["vaza", "sai"])
    async def leaveCall(self, ctx):
        current_call = ctx.voice_client
        if current_call:
            self.ping_list.remove(current_call.channel.id)
            await current_call.disconnect()
            await ctx.reply("ok <:cat:1264072257433632789>")
            print(f'Bot has disconnected on demand from "{current_call.channel.name}", in the "{current_call.channel.guild.name}" guild')
        else:
            await ctx.reply("eu nem to em call uai")
    
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user and before.channel and not after.channel and before.channel.id in self.ping_list:
            self.ping_list.remove(before.channel.id)
            print(f'Bot has been forced out of "{before.channel.name}", in the "{before.channel.guild.name}" guild')
    
    
    async def keep_connection_alive(self, voice_client):
        self.ping_list.append(voice_client.channel.id)
        
        while voice_client.channel.id in self.ping_list:
            try:
                await voice_client.channel.guild.me.edit(nick="Autista")
                print(f"Ping! in '{voice_client.channel.guild.name}'")
            except nextcord.ClientException:
                pass
            await asyncio.sleep(15)




def setup(bot):
    bot.add_cog(VoiceChatCommands(bot))