import functools, os, discord

from typing import Any, Awaitable, Callable, List, Tuple
from Modules.database_manager import DatabaseManager
from discord.ext.commands import Context

class Permission:
    database: DatabaseManager = DatabaseManager()
    
    # Class Methods
    @classmethod
    async def database_init(cls):
        await cls.database.setup(
            structure={
                'permissionTaggedRoles': {
                    'role_id': 'INTEGER',
                    'category': 'TEXT',
                    'server_id': 'INTEGER',
                }
        })
    
    
    @classmethod
    async def _fetch_roles_from_database(cls, ctx: Context, category):
        all_category = 'ALL' in category
        
        query = await cls._build_query(all_category, category)
        parameters = await cls._build_parameters(ctx, all_category, category)
        
        return await cls.database.fetchall(query, parameters)
    
    
    # private functions
    @staticmethod
    async def _build_query(all: bool, category: Tuple[str]):
        query = "SELECT role_id FROM permissionTaggedRoles WHERE "
        
        if not all:
            query += "category IN ({}) AND ".format(', '.join(['?'] * len(category)))
        
        query += "server_ID IN (?, ?)"
        
        return query
    
    
    @staticmethod
    async def _build_parameters(ctx: Context, all: bool, category: Tuple[str]):
        parameters: List[str] = []
        
        if not all:
            parameters += [*category]
        
        parameters += [ctx.guild.id, 0]
        
        return tuple(parameters)



# functions (that may be used)
async def is_user_role_tagged(ctx: Context, *category):
    blacklisted_roles = await Permission._fetch_roles_from_database(ctx, category)
    
    return any(user_role.id == blacklisted_role[0] for blacklisted_role in blacklisted_roles for user_role in ctx.author.roles)

async def is_moderator(ctx: Context | discord.Message):
    return ctx.author.guild_permissions.administrator

async def is_bot_developer(ctx: Context):
    bot_developer_id = os.environ['BOT_DEV_DISCORD_ID']
    return ctx.author.id == int(bot_developer_id)



# template
def _generic_decorator(
    check: Callable[..., Awaitable[bool]], 
    *args, 
    rejection_message: str = None, 
    invert: bool = False
    ):
    if invert:
        async def check_func(ctx, *args):
            return not await check(ctx, *args)
    else:
        async def check_func(ctx, *args):
            return await check(ctx, *args)
    
    if rejection_message:
        async def reply(ctx: Context):
            await ctx.reply(rejection_message)
    else:
        async def reply(ctx: Context):
            return
    
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx: Context, *func_args, **func_kwargs):
            if await check_func(ctx, *args):
                return await func(self, ctx, *func_args, **func_kwargs)
            else:
                await reply(ctx)
        
        return wrapper
    return decorator



# decorators
def moderator(rejection_message: str = None):
    return _generic_decorator(is_moderator, rejection_message=rejection_message)

def developer(rejection_message: str = None):
    return _generic_decorator(is_bot_developer, rejection_message=rejection_message)


def role_blacklisted(*category: str, rejection_message: str = None):
    return _generic_decorator(
        is_user_role_tagged,
        *category,
        rejection_message=rejection_message,
        invert = True
    )

def role_whitelisted(*category: str, rejection_message: str = None):
    return _generic_decorator(
        is_user_role_tagged,
        *category,
        rejection_message=rejection_message,
        invert = False
    )