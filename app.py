import nextcord
import sqlite3
import os

from nextcord import Intents
from nextcord.ext import commands
 
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=['aproveita e ', 'Aproveita e '], intents=intents)

GeneralData = sqlite3.connect('GeneralBotData.db')
Cursor = GeneralData.cursor()
GeneralData.execute("CREATE TABLE IF NOT EXISTS storedLocations(channel INT, server INT)")
GeneralData.execute("CREATE TABLE IF NOT EXISTS communityNotepad(message STR, author_ID INT, server_ID INT)")

async def getEmojis():
    main_server = await bot.fetch_guild(1263933229367562251)
    if main_server:
        emojis = main_server.emojis
    return emojis

# Sistema de bloco de notas comunitario
# Comando de anotar
@bot.command(name = "notePadWrite", aliases = ["anota"])
async def communityNotepadFunction(ctx, a1, a2, *, msg):
    if a1 == "pra" and a2 == "mim":
        authorID = ctx.author.id
        serverID = ctx.guild.id
        query = "INSERT INTO communityNotepad VALUES (?, ?, ?)"
        Cursor.execute(query, (msg, authorID, serverID))
        GeneralData.commit()       
        await ctx.reply(f"Anotado <:cat:1264072257433632789>")

# Comando de mostrar
@bot.command(name = "ShowNotePad", aliases = ["mostre", "mostra", "apresente-me"])
async def showNotepad(ctx, *, a1):
    match a1.strip():
        case "as anotações"|"as anotacoes"|"as anotação"|"as anotacao"|"as notas"|"as nota":
            query = "SELECT message, author_ID FROM communityNotepad WHERE server_ID = ?"
            data = Cursor.execute(query, (ctx.guild.id,)).fetchall()
            if len(data) == 0:
                await ctx.send(f"O {ctx.guild.name} tem uma incrível quantidade de 0 notas feitas")
            else:
                for x in data:
                    author = await bot.fetch_user(x[1])
                    await ctx.send(f"- \"{x[0]}\"\nAutor: {author}")

        case "minhas anotação"|"as minhas anotação"|"as minha anotação"|"as minhas anotações"|"minhas anotações"|"minhas nota"|"pra mim":
            query = "SELECT message FROM communityNotepad WHERE author_ID = ? AND server_ID = ?"
            data = Cursor.execute(query, (ctx.author.id, ctx.guild.id)).fetchall()

            if len(data) == 0:
                await ctx.reply("Tu n tem nota feita :thumbsup:")
            else:
                for i, x in enumerate(data):
                    await ctx.send(f"{i} - \"{x[0]}\"")

# Comando de deletar nota
@bot.command(name = "deleteNotePad", aliases = ["deleta", "apague", "acabe-lhe", "descombule-se", "evaporize-se", "mate", "mata"])
async def deleteNote(ctx, *, i):

    if i == "TUDO":
        query = "DELETE FROM communityNotepad WHERE author_ID = ? AND server_ID = ?"
        Cursor.execute(query, (ctx.author.id, ctx.guild.id))
        GeneralData.commit()
        await ctx.reply("Tá tudo morto agora")
    
    else:
        queryfetch = "SELECT message FROM communityNotepad WHERE author_ID = ? and server_ID = ?"
        data = Cursor.execute(queryfetch, (ctx.author.id, ctx.guild.id)).fetchall()
        toDelete = [int(x) for x in i.split(", ") if x.isdigit()]

        print(f"{toDelete}")

        if len(toDelete) != 0:

            for h, msg in enumerate(data):
            
                if h in toDelete:
                    print(f"{msg[0]}")
                    query = "DELETE FROM communityNotepad WHERE message = ? AND author_ID = ? AND server_ID = ?"
                    Cursor.execute(query, (*msg, ctx.author.id, ctx.guild.id))

            GeneralData.commit()
            await ctx.reply("Notas mortas com sucesso")
        else:
            await ctx.send("O burro tu tem q especificar os numero (baseado na sua lista de notas)")



# Otras merda

@bot.command(name = "test")
async def test(ctx):
    emojis = await getEmojis()
    for x in emojis:
        print(f"{x}")
    await ctx.author.send(f"<:trol:968658017086242897>")

# Comando de ser xingado ai que triste

@bot.command(name = "KILLYOURSELF", aliases = ["se", "vai"])
async def pongbop(ctx, *, confirm):
    if confirm in ["mata", "se fude", "si fude", "sifude", "se foder", "sifuder", "si fuder", "pro caralho", "pra merda", "catar coquinho"]:
        await ctx.reply("<:spong_bop:1264260742975197264>")

# Comando de Ajuda
@bot.command(name = "ayuda")
async def test(ctx):
    await ctx.author.send("Seguinte meu humano, pra me chamar é simples, só digitar \"aproveita e [comando]\", simples assim\n\nAgora...")
    await ctx.author.send("Pra uma listinha bem basica de comandos que eu tenho é o seguinte, nós temos:\n- ayuda = Faz eu manda os comandos\n- autista = <:trol:968658017086242897>\n- diz [frase] = ele diz uai")
    await ctx.author.send("Agora o bagui de notas lá:\n- anota pra mim [nota] = faz uma anotação\n- mostra as nota = mostra as nota de todo mundo do server\n- mostra minhas nota = mostra as suas notas no servidor (com numeração)\n- mata [numero] = deleta uma nota baseada no numero dela (refira-se ao ultimo comando)")

@bot.command(name = "autista")
async def sendImage(ctx):
    file = nextcord.File("Images/autismo.jpg", filename="autismo.png")
    await ctx.send(file=file)
    await ctx.message.delete()

@bot.command(name = "selecionarCanal", aliases = ["selecionarcanal", "channelselect", "channelSelect", "canallembrar", "LEMBRA"])
async def channelStore(ctx):

    server_id = ctx.guild.id
    query1 = "SELECT channel FROM storedLocations WHERE server = ?"
    currentChannelStored = Cursor.execute(query1, (server_id,)).fetchone()
    print(f"{currentChannelStored}")
    channel_id = ctx.channel.id
    

    if currentChannelStored == ctx.channel.id:

        await ctx.reply("O seu burro você ja ta no canal escolhido")

    elif currentChannelStored:
        
        query = "UPDATE storedLocations SET channel = ? WHERE server = ?"
        Cursor.execute(query, (channel_id, server_id))
        GeneralData.commit()
        await ctx.send("Tá to relembrano")

    else:

        query = "INSERT INTO storedLocations VALUES (?, ?)"
        Cursor.execute(query, (channel_id, server_id))
        GeneralData.commit()
        await ctx.send("Tá to lembrano")        

       
   
@bot.command(name = "diz")
async def sendMessage(ctx, *, message):
    await ctx.send(message)
    await ctx.message.delete()
        
# OTRAS COISA AINDA

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}")

    query = "SELECT * FROM storedLocations"
    data = Cursor.execute(query).fetchall()

    for x in data:
        currentServer = bot.get_guild(x[1])
        currentChannel = bot.get_channel(x[0])

        if currentChannel:
            await currentChannel.send("Boa tarde")
            print(f"Mensage mandada em: {currentServer.name}")
        else:
            print(f"O servidor {currentServer.name} não possue nenhum canal marcado")
    


if __name__ == '__main__':
    bot.run(os.environ['DISCORD_TOKEN'])
