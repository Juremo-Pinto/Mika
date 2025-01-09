from nextcord.ext import commands
from Modules.quick_cache import QuickCache
from Modules.database_manager import DatabaseManager

from typing import Callable

class CommunityNotepad(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = DatabaseManager(initialize=False)


    @commands.command(name = "notePadWrite", aliases = ["anota"])
    async def communityNotepadFunction(self, ctx, a1, a2, *, msg = None):
        if a1 == "pra" and a2 == "mim":
            if msg is not None:
                author_id = ctx.author.id
                server_id = ctx.guild.id
                query = "INSERT INTO communityNotepad VALUES (?, ?, ?)"
                await self.database.commit(query, (msg, author_id, server_id)) 
                await ctx.reply(f"Anotado <:cat:1264072257433632789>")
            else:
                await ctx.reply("Anotar o que porra")


    # Comando geral de mostrar
    @commands.command(name = "showInfo", aliases = ["mostre", "mostra", "apresente-me"])
    async def show_notepad(self, ctx, *, a1 = None):
        if a1 is None:
            await ctx.reply("Mostrar o que, porra")
            return
        
        match a1.strip():
            case "as anotações"|"as anotacoes"|"as anotação"|"as anotacao"|"as notas"|"as nota":
                await self.show_all_notes(ctx)
                
            case "minhas anotação"|"as minhas anotação"|"as minha anotação"|"as minhas anotações"|"minhas anotações"|"minhas nota"|"pra mim":
                await self.show_user_notes(ctx)
                
            case _:
                await ctx.reply("porra é isso")


    async def show_all_notes(self, ctx):
        query = "SELECT message, author_ID FROM communityNotepad WHERE server_ID = ?"
        data = await self.database.fetchall(query, (ctx.guild.id,))
        
        if len(data) == 0:
            await ctx.send(f"Que nota? (não tem nenhuma)")
            return
        
        result = []
        cache = QuickCache()
        
        async def fetch_author(author_id):
            return await self.bot.fetch_user(author_id)
        
        for message in data:
            author = await cache.get_or_compute(message[1], fetch_author)
            result.append(f"- \"{message[0]}\"\nAutor: {author}")
        
        await ctx.send("\n".join(result))


    async def show_user_notes(self, ctx):
        query = "SELECT message FROM communityNotepad WHERE author_ID = ? AND server_ID = ?"
        data = await self.database.fetchall(query, (ctx.author.id, ctx.guild.id))
        
        if len(data) == 0:
            await ctx.reply("Tu n tem nota feita :thumbsup:")
            return
        
        result = []
        for i, x in enumerate(data):
            result.append(f"{i} - \"{x[0]}\"")
        
        await ctx.send("\n".join(result))



    # Comando de deletar nota
    @commands.command(name = "deleteNotePad", aliases = ["mata", "MATA"])
    async def delete_note(self, ctx, *, i):
        if i == "TUDO":
            delete_all_query = "DELETE FROM communityNotepad WHERE author_ID = ? AND server_ID = ?"
            await self.database.commit(delete_all_query, (ctx.author.id, ctx.guild.id))
            await ctx.reply("Tá tudo morto agora")
        
        else:
            fetch_user_notes_query = "SELECT message FROM communityNotepad WHERE author_ID = ? and server_ID = ?"
            
            data = await self.database.fetchall(fetch_user_notes_query, (ctx.author.id, ctx.guild.id))
            
            notes_to_delete = [int(number.strip()) for number in i.split(",") if number.strip().isdigit()]
            
            if len(notes_to_delete) != 0:
                for row, message in enumerate(data):
                    if row in notes_to_delete:
                        delete_notes_query = "DELETE FROM communityNotepad WHERE message = ? AND author_ID = ? AND server_ID = ?"
                        await self.database.execute(delete_notes_query, (*message, ctx.author.id, ctx.guild.id))
                
                await self.database.commit()
                await ctx.reply("Notas mortas com sucesso")
            else:
                await ctx.send("O burro tu tem q especificar os numero (baseado na sua lista de notas)")


def setup(bot):
    bot.add_cog(CommunityNotepad(bot))