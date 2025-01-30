import asyncio
import os
from typing import Tuple

from Modules.database_manager import DatabaseManager

class RolePermissionHandler:
    def __init__(self, *category: str):
        self.category = category
        
        self.is_all_categories = 'ALL' in self.category
        
        self.database = DatabaseManager()
        
        task = self.database.setup(structure={
            'permissionTaggedRoles': {
                'role': 'TEXT',
                'category': 'TEXT',
                'server_ID': 'INTEGER',
            }
        })
        asyncio.run(task)
    
    
    async def _build_query(self):
        query = "SELECT role FROM permissionTaggedRoles WHERE "
        
        if not self.is_all_categories:
            query += "category IN ({}) AND ".format(', '.join(['?'] * len(self.category)))
        
        query += "server_ID IN (?, ?)"
        
        return query
    
    
    async def _build_parameters(self, ctx):
        parameters = []
        
        if not self.is_all_categories:
            parameters += [*self.category]
        
        parameters += [ctx.guild.id, 0]
        
        return tuple(parameters)
    
    
    async def _fetch_roles_from_database(self, ctx):
        blacklisted_roles_query = await self._build_query()
        parameters = await self._build_parameters(ctx)
        
        return await self.database.fetchall(blacklisted_roles_query, parameters)
    
    
    async def is_user_role_tagged(self, ctx):
        blacklisted_roles = await self._fetch_roles_from_database(ctx)
        
        return any(user_role.name == blacklisted_role[0] for blacklisted_role in blacklisted_roles for user_role in ctx.author.roles)



class PermissionUtils:
    @staticmethod
    async def is_moderator(ctx):
        return ctx.author.guild_permissions.administrator
    
    async def is_bot_developer(ctx):
        bot_developer_id = os.environ['MINE_DISCORD_ID']
        return ctx.author.id == int(bot_developer_id)