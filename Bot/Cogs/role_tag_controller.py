import nextcord

from nextcord.ext import commands
from Modules.command_manipulation.command_extension import command_extension
from Modules.information_manager import InformationManager
from Modules.database_manager import DatabaseManager
from Modules.command_permissions import is_bot_developer, moderator

class RolePermissionController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = DatabaseManager()
        self.info_manager = InformationManager(self.bot)
    
    
    
    @commands.command(name="permissão")
    @command_extension("de cargo", "pro cargo")
    @moderator()
    async def mark_role_permission(self, ctx, role_mention = None, category = None, *, other = None):
        role_object = await self._is_command_valid(ctx, role_mention, category)
        
        if role_object is None:
            return
        
        global_role = other is not None and 'global-role' in other and is_bot_developer(ctx)
        
        if global_role:
            print(f'Added "{role_object.name}" role to global role permissions')
            await ctx.author.send("Adicicionado global ein ó q fóda xdxdxd")
        
        await ctx.reply("Belezura chefia")
        await self._do_a_little_storing(ctx, global_role, role_object, category)
    
    
    async def _do_a_little_storing(self, ctx, global_role, role_object, category):
        add_role_query = "INSERT INTO permissionTaggedRoles VALUES (?, ?, ?)"
        server_id = ctx.guild.id if not global_role else 0
        
        await self.database.commit(add_role_query, (role_object.name, category, server_id))
    
    
    async def _is_command_valid(self, ctx, role_mention, category):
        if role_mention is None or category is None:
            await ctx.send("Dexa de ser burro")
            return None
        
        role_object = nextcord.utils.get(ctx.guild.roles, mention=role_mention)
        
        if role_object is None:
            await ctx.send("esse cargo aí não existe não fi")
            return None
        
        return role_object
    
    
    @commands.command(name="despermissão")
    @command_extension("de cargo", "pro cargo")
    @moderator()
    async def remove_blacklist(self, ctx):
        pass
        #amanha eu faço




def setup(bot):
    bot.add_cog(RolePermissionController(bot))