import asyncio
import nextcord
from nextcord.ext import commands

class VoiceChatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ping = False
    
    @commands.command("joinCall", aliases = ["entra"])
    async def joinCall(self, ctx, a1):
        if a1 in ["ai", "ae"]:
            if hasattr(ctx.author.voice, 'channel'):
                await ctx.reply("ok <:cat:1264072257433632789>")
                await ctx.author.voice.channel.connect()
                await self.keep_connection_alive(ctx.voice_client)
            else:
                await ctx.reply("Tenta entrar na call primeiro")


    @commands.command("leaveCall", aliases = ["vaza", "sai"])
    async def leaveCall(self, ctx):
        currentCall = ctx.voice_client
        if currentCall:
            await currentCall.disconnect()
            self.ping = False
            await ctx.reply("ok <:cat:1264072257433632789>")
        else:
            await ctx.reply("eu nem to em call uai")


    async def keep_connection_alive(self, voice_client):
        self.ping = True
        while self.ping:
            try:
                await voice_client.channel.guild.me.edit(nick="Autista")
                print("Ping!")
            except nextcord.ClientException:
                pass
            await asyncio.sleep(15)




def setup(bot):
    bot.add_cog(VoiceChatCommands(bot))