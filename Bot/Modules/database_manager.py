import asyncio
import aiosqlite
from resources_path import ResourcesPath

#debug_database_path = r"D:\Quase Importante\Codegos\Python\NextCord\AutismoBOT\Bot\Resources\DataBase\GeneralBotData.db"

class DatabaseManager:
    _instances = set()
    
    def __init__(self):
        self.resources = ResourcesPath()
        self.loop = None
        
        self.database = None
        self.cursor = None
        
        asyncio.run(self.connect())
        
        self._instances.add(self)
    
    def __del__(self):
        if self.database is not None:
            self.loop.run_until_complete(self.database.close())
        
        try:
            self._instances.remove(self)
        except KeyError:
            pass
    
    
    
    async def connect(self):
        self.loop = asyncio.get_event_loop()
        
        self.database = await aiosqlite.connect(f"{self.resources('database')}/GeneralBotData.db")
        self.cursor = await self.database.cursor()
    
    
    async def disconnect(self):
        if self.database is not None:
            await self.database.close()
    
    
    @classmethod
    async def disconnect_all(cls):
        for instance in list(cls._instances):
            await instance.disconnect()
            instance.database = None
        
        cls._instances.clear()
    
    
    async def execute(self, query, parameters = None):
        return await self.cursor.execute(query, parameters)
    
    
    async def setup(self, structure, always_create = False):
        base_query = "CREATE TABLE "
        base_query += "IF NOT EXISTS " if always_create == False else ""
        
        for table in structure:
            columns = []
            
            for column in structure[table]:
                columns += [f"{column} {structure[table][column]}"]
            
            init_query = base_query + table + f'({', '.join(columns)})'
            await self.database.execute(init_query)
    
    
    async def fetchall(self, query, parameters = None):
        cursor = await self.cursor.execute(query, parameters)
        return await cursor.fetchall()
    
    
    async def fetchone(self, query, parameters = None):
        cursor = await self.cursor.execute(query, parameters)
        return await cursor.fetchone()
    
    
    async def fetchmany(self, query, parameters = None, size = None):
        cursor = await self.cursor.execute(query, parameters)
        return await cursor.fetchmany(size)
    
    
    async def commit(self, query = None, parameters = None):
        if query is not None:
            await self.cursor.execute(query, parameters)
        await self.database.commit()



async def test(db):
    await db.connect()
    #await db.commit('ALTER TABLE blacklistedRoles RENAME TO permissionTaggedRoles')

if __name__ == "__main__":
    db = DatabaseManager()
    asyncio.run(test(db))