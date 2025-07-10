import asyncio, signal
from typing import Any, Tuple

import discord
from discord.ext.commands import Bot, Context
from discord import Message, app_commands

from Modules.Logging.logger import logger
from Modules.command_permissions import is_user_role_tagged
from Modules.information_manager import InformationManager
from Modules.database_manager import DatabaseManager

class BotClient(Bot):
    def __init__(self, command_prefix, *, send_errors_to_developer_dm = False, help_command = ..., tree_cls = app_commands.CommandTree, description = None, allowed_contexts = ..., allowed_installs = ..., intents, **options):
        super().__init__(command_prefix, help_command=help_command, tree_cls=tree_cls, description=description, allowed_contexts=allowed_contexts, allowed_installs=allowed_installs, intents=intents, **options)
        
        self.info_manager = InformationManager(self)
        
        self.dev_user = None
        self.send_errors_to_developer_dm = send_errors_to_developer_dm
    
    async def load_extensions(self, *names: Tuple[str], package: Any = None):
        for name in names:
            await self.load_extension(name, package=package)
    
    async def setup_hook(self):
        self.dev_user = await self.info_manager.get_bot_dev()
        
        await self.load_extension('startup')
        
        #await bot.load_extension('Modules.command_manipulation.shared_command_system')
        #await bot.load_extension('Cogs.test')
        
        await self.load_extensions(
            'Cogs.developer_exclusive',
            'Cogs.general_commands',
            'Cogs.general_events',
            'Cogs.voice_channel',
            'Cogs.community_notepad',
            'Cogs.youtube_playback.youtube_playback',
            'Cogs.text_channel_selection',
            'Cogs.mass_message_deletion',
            'Cogs.role_tag_controller'
        )
        
        self.register_signal_handlers()
    
    
    async def close(self):
        logger.info("Disconnecting Database...")
        await DatabaseManager.disconnect()
        logger.info("Database Disconnected")
        
        logger.info("Shutting down...")
        return await super().close()
    
    
    async def on_command_error(self, context: Context, exception: Exception):
        if self.send_errors_to_developer_dm:
            await self._report_error_dm(context, exception)
        
        return await super().on_command_error(context, exception)
    
    
    async def _report_error_dm(self, context: Context, exception: Exception):
        error_type = exception.__class__.__name__
        if error_type == "CommandNotFound":
            return
        
        embed = discord.Embed(
            title="Error Caught",
            description=f"An error occurred in `{context.guild.name}`",
            color=discord.Color.red()
        )
        
        embed.add_field(name="Server", value=f"`{context.guild.name}` (ID: `{context.guild.id}`)", inline=False)
        embed.add_field(name="Channel", value=f"<#{context.channel.id}> (`{context.channel.id}`)", inline=False)
        embed.add_field(name="Invoker", value=f"{context.author} (ID: `{context.author.id}`)", inline=False)
        embed.add_field(name="Command", value=f"`{context.command}`", inline=False)
        embed.add_field(name="Error Type", value=f"`{error_type}`", inline=True)
        embed.add_field(name="Error Message", value=f"`{exception}`", inline=True)
        embed.add_field(name="Message Content", value=f"```plaintext\n{context.message.content}\n```", inline=False)
        
        embed.set_footer(text="Error Logger")
        embed.timestamp = context.message.created_at
        
        await self.dev_user.send(embed=embed)
    
    
    def register_signal_handlers(self):
        def handler(sig, frame):
            self.loop.create_task(self.close())
        
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
    
    
    async def on_message(self, message: Message):
        if message.content.startswith(tuple(await self.get_prefix(message))) and await is_user_role_tagged(await self.get_context(message), 'forbid_BOT'):
            logger.info(f'Blacklisted user "{message.author.name}" tried using bot in {message.guild.name}, {message.channel.name}')
            return
        
        await self.process_commands(message)