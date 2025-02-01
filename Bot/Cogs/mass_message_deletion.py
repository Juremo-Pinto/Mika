import asyncio
from nextcord.ext import commands

from Modules.command_permissions import PermissionUtils

class MassMessageDeletion(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message_deletion_dict = {}
    
    
    # Pra marcar
    @commands.command(name = "toMark", aliases = ["marca"])
    async def mark(self, ctx):
        if not await PermissionUtils.is_moderator(ctx):
            return
        
        channelID = ctx.channel.id
        if channelID not in self.message_deletion_dict:
            self.message_deletion_dict[channelID] = []
            self.message_deletion_dict[channelID].append(ctx.message)
            await ctx.reply("marquei meu")
        else:
            await ctx.reply("Já tá marcado")
    
    
    # Pra deletar
    @commands.command(name = "toDelete", aliases = ["deleta"])
    async def delete(self, ctx):
        if not await PermissionUtils.is_moderator(ctx):
            return
        
        channel_id = ctx.channel.id
        
        if not channel_id in self.message_deletion_dict:
            await ctx.reply("não tá marcado")
            return
        
        messages_to_delete = []
        collected_messages = self.message_deletion_dict[channel_id]
        
        async def delete_message(msg):
            try:
                await msg.delete()
            except Exception as e:
                pass
        
        for items in collected_messages:
            messages_to_delete.append(delete_message(items))
        
        await asyncio.gather(*messages_to_delete)
        del self.message_deletion_dict[channel_id]
        
        await ctx.author.send("Pronto fi")
    
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in self.message_deletion_dict:
            self.message_deletion_dict[message.channel.id].append(message)


def setup(bot):
    bot.add_cog(MassMessageDeletion(bot))