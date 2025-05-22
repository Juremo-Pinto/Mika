import asyncio, functools, os

from typing import Tuple
from Modules.utils import Utils
from Modules.database_manager import DatabaseManager

class Permission:
    database = DatabaseManager(auto_connect=False)
    
    # Class Methods
    @classmethod
    async def database_init(cls):
        await cls.database.connect()
        await cls.database.setup(
            structure={
                'permissionTaggedRoles': {
                    'role': 'TEXT',
                    'category': 'TEXT',
                    'server_ID': 'INTEGER',
                }
        })
    
    @classmethod
    async def _fetch_roles_from_database(cls, ctx, category):
        all_category = 'ALL' in category
        
        query = await Permission._build_query(all_category, category)
        parameters = await Permission._build_parameters(ctx, all_category, category)
        
        return await cls.database.fetchall(query, parameters)
    
    
    # private functions
    @staticmethod
    async def _build_query(all, category):
        query = "SELECT role FROM permissionTaggedRoles WHERE "
        
        if not all:
            query += "category IN ({}) AND ".format(', '.join(['?'] * len(category)))
        
        query += "server_ID IN (?, ?)"
        
        return query
    
    
    @staticmethod
    async def _build_parameters(ctx, all, category):
        parameters = []
        
        if not all:
            parameters += [*category]
        
        parameters += [ctx.guild.id, 0]
        
        return tuple(parameters)




# functions (that may be used)
async def is_user_role_tagged(ctx, *category):
    blacklisted_roles = await Permission._fetch_roles_from_database(ctx, category)
    
    return any(user_role.name == blacklisted_role[0] for blacklisted_role in blacklisted_roles for user_role in ctx.author.roles)

async def is_moderator(ctx):
    return ctx.author.guild_permissions.administrator

async def is_bot_developer(ctx):
    bot_developer_id = os.environ['MINE_DISCORD_ID']
    return ctx.author.id == int(bot_developer_id)



# template
def generic_decorator(check, *args, rejection_message = None, invert = False):
    if invert:
        async def check_func(ctx, *args):
            return not await check(ctx, *args)
    else:
        async def check_func(ctx, *args):
            return await check(ctx, *args)
    
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, *func_args, **func_kwargs):
            if await check_func(ctx, *args):
                return await func(self, ctx, *func_args, **func_kwargs)
            elif rejection_message:
                await ctx.reply(rejection_message)
        return wrapper
    return decorator



# decorators
def moderator(rejection_message: str = None):
    return generic_decorator(is_moderator, rejection_message=rejection_message)

def developer(rejection_message: str = None):
    return generic_decorator(is_bot_developer, rejection_message=rejection_message)


def role_blacklisted(*category, rejection_message: str = None):
    return generic_decorator(
        is_user_role_tagged,
        *category,
        rejection_message=rejection_message,
        invert = True
    )

def role_whitelisted(*category, rejection_message: str = None):
    return generic_decorator(
        is_user_role_tagged,
        *category,
        rejection_message=rejection_message,
        invert = False
    )