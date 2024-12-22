from nextcord.ext import commands
from Modules.database_manager import DatabaseManager

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
    @commands.command(name = "ShowInfo", aliases = ["mostre", "mostra", "apresente-me"])
    async def showNotepad(self, ctx, *, a1 = None):
        match a1.strip():
            case "as anotações"|"as anotacoes"|"as anotação"|"as anotacao"|"as notas"|"as nota":
                query = "SELECT message, author_ID FROM communityNotepad WHERE server_ID = ?"
                data = await self.database.fetchall(query, (ctx.guild.id,))
                
                if len(data) == 0:
                    await ctx.send(f"O {ctx.guild.name} tem uma incrível quantidade de 0 notas feitas")

                else:
                    result = []
                    for x in data:
                        author = await self.bot.fetch_user(x[1])
                        result.append(f"- \"{x[0]}\"\nAutor: {author}")

                    await ctx.send("\n".join(result))

            case "minhas anotação"|"as minhas anotação"|"as minha anotação"|"as minhas anotações"|"minhas anotações"|"minhas nota"|"pra mim":
                query = "SELECT message FROM communityNotepad WHERE author_ID = ? AND server_ID = ?"
                data = await self.database.fetchall(query, (ctx.author.id, ctx.guild.id))

                if len(data) == 0:
                    await ctx.reply("Tu n tem nota feita :thumbsup:")

                else:
                    result = []

                    for i, x in enumerate(data):
                        result.append(f"{i} - \"{x[0]}\"")
                    await ctx.send("\n".join(result))
            case _:
                await ctx.reply("Mostrar o que, porra")


    # Comando de deletar nota
    @commands.command(name = "deleteNotePad", aliases = ["mata", "MATA"])
    async def deleteNote(self, ctx, *, i):

        if i == "TUDO":
            query = "DELETE FROM communityNotepad WHERE author_ID = ? AND server_ID = ?"
            await self.database.commit(query, (ctx.author.id, ctx.guild.id))
            await ctx.reply("Tá tudo morto agora")
        
        else:
            queryfetch = "SELECT message FROM communityNotepad WHERE author_ID = ? and server_ID = ?"
            
            data = await self.database.fetchall(queryfetch, (ctx.author.id, ctx.guild.id))
            
            toDelete = [int(x) for x in i.split(", ") if x.isdigit()]

            if len(toDelete) != 0:
                for h, msg in enumerate(data):
                    if h in toDelete:
                        query = "DELETE FROM communityNotepad WHERE message = ? AND author_ID = ? AND server_ID = ?"
                        await self.database.execute(query, (*msg, ctx.author.id, ctx.guild.id))

                await self.database.commit()
                await ctx.reply("Notas mortas com sucesso")
            else:
                await ctx.send("O burro tu tem q especificar os numero (baseado na sua lista de notas)")



def setup(bot):
    bot.add_cog(CommunityNotepad(bot))