# bot_utilities.py

import nextcord

class bot_utilities:
    """General utility functions for the bot.
    """
    def __init__(self, bot_object: nextcord.Client):
        """
        Args:
            bot_object (nextcord.Client): The nextcord bot object that represents the bot
        """
        self.bot = bot_object
    
    async def fetch_server_by_name(self, desired_server_name: str) -> nextcord.Guild | None:
        """Returns a server object by its name, returns None if no server is found

        Args:
            desired_server_name (str): the server name to search for

        Returns:
            Guild: the server object if found
            None: if no server is found
        """
        servers = self.bot.guilds

        print('adquiring the server')

        for server in servers:
            if server.name == desired_server_name:
                return server

        return None


    async def fetch_member_by_name(self, member_name: str) -> nextcord.Member | None:
        """Returns a member object by its name, returns None if no member is found

        Args:
            member_name (str): the member name to search for

        Returns:
            Member: the member object if found
            None: if no member is found
        """
        servers = self.bot.guilds
        
        for server in servers:
            memberlist = await server.fetch_members().flatten()
            
            for member in memberlist:
                if member.name == member_name:
                    return member
        
        return None


    async def fetch_member_by_id(self, member_id: int) -> nextcord.Member | None:
        """Returns a member object by its id, returns None if no member is found

        Args:
            member_id (int): the member id to search for

        Returns:
            Member: the member object if found
            None: if no member is found
        """
        servers = self.bot.guilds
        
        for server in servers:
            member = await server.fetch_member(member_id)
            if member:
                return member
            
        return None