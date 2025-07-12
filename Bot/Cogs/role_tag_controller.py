import discord

from discord.ext import commands
from Modules.command_manipulation.command_extension import command_extension
from Modules.information_manager import InformationManager
from Modules.database_manager import DatabaseManager
from Modules.command_permissions import developer, is_bot_developer, moderator
from Modules.Logging.logger import logger

class RolePermissionController(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = DatabaseManager()
        self.info_manager = InformationManager(self.bot)
    
    async def cog_load(self):
        logger.info(f"Cog Loaded: {self.__cog_name__}")
    
    @commands.command(name="permissão", aliases = ["tag"])
    @command_extension("de cargo", "pro cargo", "cargo")
    @moderator()
    async def tag_role(self, ctx: commands.Context, cargo_str: str = None, category: str = None, *, other: str = None):
        cargo = await self._is_command_valid(ctx, cargo_str, category)
        
        if cargo is None:
            return
        
        global_role: bool = other is not None and 'global-role' in other and await is_bot_developer(ctx)
        
        if global_role:
            logger.info(f'Added "{cargo.name}" role to global role permissions')
            await ctx.author.send("Adicicionado global ein ó q fóda xdxdxd")
        
        await ctx.reply("Belezura chefia")
        await self._do_a_little_storing(ctx, global_role, cargo, category)
    
    
    async def _do_a_little_storing(self, ctx: commands.Context, global_role: bool, cargo: discord.Role, category: str):
        add_role_query = "INSERT INTO permissionTaggedRoles VALUES (?, ?, ?)"
        server_id = ctx.guild.id if not global_role else 0
        
        await self.database.commit(add_role_query, (cargo.id, category, server_id))
    
    
    async def _is_command_valid(self, ctx: commands.Context, cargo_str: str, category: str) -> discord.Role | None:
        if cargo_str is None or category is None:
            await ctx.send("Dexa de ser burro")
            return None
        
        cargo = discord.utils.get(ctx.guild.roles, mention=cargo_str)
        
        if cargo is None:
            await ctx.send("esse cargo aí não existe não fi")
        
        return cargo
    
    
    @commands.command(name="despermissão", aliases = ["untag"])
    @command_extension("de cargo", "pro cargo", "cargo")
    @moderator()
    async def untag(self, ctx: commands.Context, cargo: str = None, category: str = None):
        cargo: discord.Role = await self._is_command_valid(ctx, cargo, category)
        
        if cargo is None:
            return
        
        query = "DELETE FROM permissionTaggedRoles WHERE role_id = ? AND category = ? and server_id = ?"
        
        role_id = cargo.id
        server_id = ctx.guild.id
        
        params = (role_id, category, server_id)
        await self.database.commit(query, params)
        await ctx.reply("Okiiiii")
    
    
    
    @commands.command(name="get-role-id")
    @developer()
    async def role_id(self, ctx: commands.Context, cargo_str: str):
        cargo = discord.utils.get(ctx.guild.roles, mention=cargo_str)
        logger.info(cargo.id)



async def setup(bot: commands.Bot):
    await bot.add_cog(RolePermissionController(bot))