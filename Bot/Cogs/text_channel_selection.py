import asyncio
from nextcord.ext import commands
from Modules.database_manager import DatabaseManager

from Modules.command_permissions import PermissionUtils

class TextChannelSelection(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = DatabaseManager()
        self.command_map = {
        "O BOA TARDE": 0,
        # "O CANAL DE MUSICA": 1  --WIP, not implemented and im too lazy, someday maybe
        # for now thats it
        }
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.database.connect()
    
    @commands.command(name = "selecionarCanal", aliases = ["selecionarcanal", "channelselect", "channelSelect", "canallembrar", "LEMBRA", 'lembra'])
    async def channelStore(self, ctx, *, msg = None):
        if not await PermissionUtils.is_moderator(ctx):
            return
        
        if msg is None:
            await ctx.send("que, lembrar do que?")
        
        index = self.command_map.get(msg, None)
        server_id = ctx.guild.id
        channel_id = ctx.channel.id
        
        if index is not None:
            query1 = "SELECT channel_ID FROM storedLocations WHERE server_ID = ? AND general_ID = ?"
            data = await self.database.fetchone(query1, (server_id, index))
            
            if data:
                currentChannelStored, = data
                
                if currentChannelStored == channel_id:
                    await ctx.reply("O seu burro você ja ta no canal escolhido")
                
                else:                
                    query = "UPDATE storedLocations SET channel = ? WHERE server_ID = ?"
                    await self.database.commit(query, (channel_id, server_id))
                    await ctx.send("Tá to relembrano")
            
            else:
                query = "INSERT INTO storedLocations VALUES (?, ?, ?)"
                await self.database.commit(query, (channel_id, server_id, index))
                await ctx.send("Tá to lembrano")
    
    
    
    @commands.command(name = "esquecerCanal", aliases = ["esquecercanal", "ESQUECE", "ESQUEÇE", "esquece", "esqueçe"])
    async def channelForget(self, ctx, *, msg = None):
        if not await PermissionUtils.is_moderator(ctx):
            return
        
        if msg is None:
            await ctx.send("que, esquecer o que?")
        
        index = self.command_map.get(msg, None)
        if index is not None:
            channel_id = ctx.channel.id
            server_id = ctx.guild.id
            query = "SELECT channel FROM storedLocations WHERE server_ID = ? AND general_ID = ?"
            
            data = await self.database.fetchone(query, (server_id, index))
            
            if data:
                channel = await self.bot.fetch_channel(*data)
                confirmation_message = await ctx.send(f"certeza que quer deletar isso do canal {channel.name}")
                await confirmation_message.add_reaction("<:cat:1264072257433632789>")
                
                def checkForReaction(reaction, author):
                    return author == ctx.author and str(reaction.emoji) == "<:cat:1264072257433632789>"
                
                try:
                    await self.bot.wait_for("reaction_add", timeout=5.0, check=checkForReaction)
                    
                    query2 = "DELETE FROM storedLocations WHERE channel = ? AND server_ID = ? AND general_ID = ?"
                    await self.database.commit(query2, (channel_id, server_id, index))
                    await ctx.send("Tá to esquecendo")
                except asyncio.TimeoutError:
                    await ctx.send("Esqueci oq eu ia fazer fr")
            
            else:
                await ctx.reply("meu mano não tem canal selecionado pra isso aqui nesse server")


def setup(bot):
    bot.add_cog(TextChannelSelection(bot))