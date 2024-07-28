import nextcord
import sqlite3
import os
import yt_dlp
import asyncio
import random

from nextcord import Intents
from nextcord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
 
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=['aproveita e ', 'Aproveita e '], intents=intents)

scheduler = AsyncIOScheduler()

GeneralData = sqlite3.connect('GeneralBotData.db')
Cursor = GeneralData.cursor()
GeneralData.execute("CREATE TABLE IF NOT EXISTS storedLocations(channel INT, server INT, general_ID)")
GeneralData.execute("CREATE TABLE IF NOT EXISTS communityNotepad(message STR, author_ID INT, server_ID INT)")

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'fragment_retries': 5,
}

ytdl_extractor_options = {
    'extract_flat': True,
    'quiet': True,
    'noplaylist': False
}

ffmpeg_format_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)
ytdlInfoExtractor = yt_dlp.YoutubeDL(ytdl_extractor_options)

class YTDLSource(nextcord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, shuffle = False, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        info, _ = await cls.get_info(url, True, shuffle, loop=loop)

        data = await asyncio.wait_for(loop.run_in_executor(None, lambda: ytdl.extract_info(info['url'] if 'url' in info else info['original_url'], download=False)), timeout=30)

        filename = data['url']
        return cls(nextcord.FFmpegPCMAudio(filename, **ffmpeg_format_options), data=data)
    
    @classmethod
    async def get_info(cls, url, addToQueue = False, shuffle = False, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        info = await asyncio.wait_for(loop.run_in_executor(None, lambda: ytdlInfoExtractor.extract_info(url, download=False)), timeout=15)
        addedToQueue = False

        if 'entries' in info and info['entries']:
            if shuffle:
                random.shuffle(info['entries'])
            if addToQueue:
                for entry in info['entries'][1:]:
                    musicQueue.append([entry['url'], entry['title']])
                addedToQueue = True
            info = info['entries'][0]        
             
        return info, addedToQueue



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


# Comando geral de mostrar
@bot.command(name = "ShowInfo", aliases = ["mostre", "mostra", "apresente-me"])
async def showNotepad(ctx, *, a1):
    match a1.strip():
        case "as anotações"|"as anotacoes"|"as anotação"|"as anotacao"|"as notas"|"as nota":
            query = "SELECT message, author_ID FROM communityNotepad WHERE server_ID = ?"
            data = Cursor.execute(query, (ctx.guild.id,)).fetchall()
            if len(data) == 0:

                await ctx.send(f"O {ctx.guild.name} tem uma incrível quantidade de 0 notas feitas")

            else:

                result = []
                for x in data:
                    author = await bot.fetch_user(x[1])
                    result.append(f"- \"{x[0]}\"\nAutor: {author}")

                await ctx.send("\n".join(result))

        case "minhas anotação"|"as minhas anotação"|"as minha anotação"|"as minhas anotações"|"minhas anotações"|"minhas nota"|"pra mim":
            query = "SELECT message FROM communityNotepad WHERE author_ID = ? AND server_ID = ?"
            data = Cursor.execute(query, (ctx.author.id, ctx.guild.id)).fetchall()

            if len(data) == 0:

                await ctx.reply("Tu n tem nota feita :thumbsup:")

            else:

                result = []

                for i, x in enumerate(data):
                    result.append(f"{i} - \"{x[0]}\"")
                await ctx.send("\n".join(result))
        
        case "as musica"|"a lista de musicas"|"as musicas":
            if len(musicQueue) > 0 and musicQueue[0]:
                message = f"- **{currentlyPlaying}**\n"
                for song in musicQueue:
                    songMessage = f"- {song[1]}\n"
                    if len(message) + len(songMessage) > 2000:
                        await ctx.send(message)
                        message = songMessage
                    else:
                        message += songMessage
                ctx.send(message)
            elif currentlyPlaying is not None:
                await ctx.send(f"- **{currentlyPlaying}**")
            else:
                await ctx.reply("a fila ta vazia fi")


# Comando de deletar nota
@bot.command(name = "deleteNotePad", aliases = ["mata", "MATA"])
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

        if len(toDelete) != 0:

            for h, msg in enumerate(data):
            
                if h in toDelete:
                    query = "DELETE FROM communityNotepad WHERE message = ? AND author_ID = ? AND server_ID = ?"
                    Cursor.execute(query, (*msg, ctx.author.id, ctx.guild.id))

            GeneralData.commit()
            await ctx.reply("Notas mortas com sucesso")
        else:
            await ctx.send("O burro tu tem q especificar os numero (baseado na sua lista de notas)")

# YOUTUBE HELL YEAHHH

@bot.command("joinCall", aliases = ["entra"])
async def joinCall(ctx, a1):
    if a1 in ["ai", "ae"]:
        if hasattr(ctx.author.voice, 'channel'):
            await ctx.reply("ok <:cat:1264072257433632789>")
            await ctx.author.voice.channel.connect()
        else:
            await ctx.reply("Tenta entrar na call primeiro")



@bot.command("leaveCall", aliases = ["vaza", "sai"])
async def leaveCall(ctx):
    currentCall = ctx.voice_client
    if currentCall:
        await currentCall.disconnect()
        await ctx.reply("ok <:cat:1264072257433632789>")
    else:
        await ctx.reply("eu nem to em call uai")



musicQueue = []
currentlyPlaying = None



@bot.command("play", aliases = ["toca"])
async def requestHandler(ctx, *, url):
    data = url.split(' ')
    shuffle = False
    if len(data) == 2:
        if data[1] == "aleatorio":
            shuffle = True
    
    VCClient = ctx.voice_client
    if VCClient:
        await ctx.send("ok calma")

        isNew = not VCClient.is_playing() and len(musicQueue) == 0 and currentlyPlaying is None
        wasAdded = False

        try:
            info, wasAdded = await YTDLSource.get_info(data[0], not isNew, shuffle, loop=bot.loop)
        except asyncio.TimeoutError:
            info = {'title': 'PlaceHolder'}

        if not wasAdded:
            musicQueue.append([data[0], info['title']])
            
        if isNew:
            bot.loop.create_task(playSong(ctx, VCClient, shuffle)) 
        else:
            await ctx.reply(f"botado na playlist")

    else:
        await ctx.send("Tenta entra na call primeiro")

    await ctx.message.delete()

async def playSong(ctx, VC, shuffle = False):
    if len(musicQueue) > 0 and musicQueue[0]:
        global currentlyPlaying
        songToPlay = musicQueue.pop(0)

        try:          
            async with ctx.typing():
                next_song = songToPlay[0]
                player = await YTDLSource.from_url(next_song, shuffle, loop=bot.loop)
                await ctx.send(f"Tocano: **{player.title}**")
                currentlyPlaying = player.title

                if not VC.is_connected() and hasattr(ctx.author.voice, 'channel'):
                    await ctx.author.voice.channel.connect()

                VC.play(player, after=lambda e: bot.loop.create_task(playSong(ctx, VC)))
        except (yt_dlp.utils.DownloadError, asyncio.TimeoutError) as e:
                await ctx.send("deu ruim, proxima música")
                bot.loop.create_task(playSong(ctx, VC))
    else:
        await ctx.send("Cabô a fila")
        currentlyPlaying = None


@bot.command("skip", aliases = ["skipa", "pula"])
async def skip(ctx):
    VC = ctx.voice_client
    if VC:
        VC.stop()
        await ctx.reply("tá")


@bot.command("playing", aliases = ["diz", "fala"])
async def playing(ctx, *, msg):
    if msg in ["oq tá tocando", "oq tá tocando", "oq tá tocano", "oq ta tocano", "oq ta tocando", "a musica que esta sendo reproduzida nesse momento"]:  
        global currentlyPlaying
        if currentlyPlaying:
            await ctx.reply(f"**{currentlyPlaying}**")
        else:
            await ctx.reply("nada")

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user and before.channel and not after.channel:
        global musicQueue
        global currentlyPlaying
        musicQueue = []
        currentlyPlaying = None
            
        

# Otras merda

@bot.command(name = "test")
async def test(ctx):
    #emojis = await getEmojis()
    #for x in emojis:
    #    print(f"{x}")
    await ctx.author.send(f"<:trol:968658017086242897>")

# Comando de ser xingado ai que triste

@bot.command(name = "xingamento", aliases = ["si", "se", "vai"])
async def pongbop(ctx, *, confirm):
    if confirm in ["mata", "mata mlk", "se fude", "si fude", "sifude", "se foder", "sifuder", "si fuder", "pro caralho", "pra merda", "catar coquinho"]:
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



commandMap = {
    "O BOA TARDE": 0,
    "O CANAL DE MUSICA": 1
    # for now thats it
}



@bot.command(name = "selecionarCanal", aliases = ["selecionarcanal", "channelselect", "channelSelect", "canallembrar", "LEMBRA"])
async def channelStore(ctx, *, msg):
    index = commandMap.get(msg, None)
    server_id = ctx.guild.id
    channel_id = ctx.channel.id

    if index is not None:
        query1 = "SELECT channel FROM storedLocations WHERE server = ? AND general_ID = ?"
        data = Cursor.execute(query1, (server_id, index)).fetchone()

        if data:
            currentChannelStored, = data

            if currentChannelStored == channel_id:

                await ctx.reply("O seu burro você ja ta no canal escolhido")

            else:                
                query = "UPDATE storedLocations SET channel = ? WHERE server = ?"
                Cursor.execute(query, (channel_id, server_id))
                GeneralData.commit()
                await ctx.send("Tá to relembrano")

        else:

            query = "INSERT INTO storedLocations VALUES (?, ?, ?)"
            Cursor.execute(query, (channel_id, server_id, index))
            GeneralData.commit()
            await ctx.send("Tá to lembrano")



@bot.command(name = "esquecerCanal", aliases = ["esquecercanal", "ESQUECE", "ESQUEÇE"])
async def channelForget(ctx, *, msg):
    index = commandMap.get(msg, None)
    if index is not None:
        channel_id = ctx.channel.id
        server_id = ctx.guild.id
        query = "SELECT channel FROM storedLocations WHERE server = ? AND general_ID = ?"
        data = Cursor.execute(query, (server_id, index)).fetchone()

        if data:
            chnl = await bot.fetch_channel(*data)
            confirmMSG = await ctx.send(f"certeza que quer deletar isso do canal {chnl.name}")
            await confirmMSG.add_reaction("<:cat:1264072257433632789>")

            def checkForReaction(reaction, author):
                return author == ctx.author and str(reaction.emoji) == "<:cat:1264072257433632789>"
            
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=5.0, check=checkForReaction)

                query2 = "DELETE FROM storedLocations WHERE channel = ? AND server = ? AND general_ID = ?"
                Cursor.execute(query2, (channel_id, server_id, index))
                GeneralData.commit()
                await ctx.send("Tá to esquecendo")
            except asyncio.TimeoutError:
                await ctx.send("Esqueci oq eu ia fazer fr")

        else:
            await ctx.reply("meu mano não tem canal selecionado pra isso aqui nesse server")



@bot.command(name = "repita")
async def sendMessage(ctx, *, message):
    await ctx.send(message)
    await ctx.message.delete()


markedMessages = {}


# Pra marcar
@bot.command(name = "toMark", aliases = ["marca"])
async def toMark(ctx):
    channelID = ctx.channel.id
    if channelID not in markedMessages:
        markedMessages[channelID] = []
        markedMessages[channelID].append(ctx.message)
        await ctx.reply("marquei meu")


# Pra deletar
@bot.command(name = "toDelete", aliases = ["deleta"])
async def toDelete(ctx):
    channelID = ctx.channel.id
    finalMsgsToDel = []
    if channelID in markedMessages:
        MsgToDel = markedMessages[channelID]
        for items in MsgToDel:
            try:
                await items.channel.fetch_message(items.id)
                finalMsgsToDel.append(items)
            except:
                pass
        await asyncio.gather(*[msg.delete() for msg in finalMsgsToDel])
        del markedMessages[channelID]
        await ctx.author.send("Pronto")


@bot.event
async def on_message(message):
    if message.channel.id in markedMessages:
        markedMessages[message.channel.id].append(message)

    if str.lower(message.content) == 'fat fuck' and message.author.id != bot.user.id:
        await message.channel.send('fat fuck') 
    
    await bot.process_commands(message)

# OTRAS COISA AINDA

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}")

    query = "SELECT channel, server FROM storedLocations WHERE general_ID = 0"
    data = Cursor.execute(query).fetchall()

    for x in data:
        currentServer = bot.get_guild(x[1])
        currentChannel = bot.get_channel(x[0])

        if currentChannel:
            await currentChannel.send("Boa tarde")
            print(f"Mensage mandada em: {currentServer.name}")
        else:
            print(f"O servidor {currentServer.name} não possue nenhum canal marcado")

    if random.randint(1, 3) == 1:
        await performAMinusculeAmountOfDespicableActions()

    await asyncio.sleep(random.randint(60, 150))

    scheduler.add_job(theTrolling_Handler, 'interval', minutes = 1)
    scheduler.start()



Audios = [
    'A bobina.mp3',
    'Aii meu piruuu.mp3',
    'mae tem cafe.mp3',
    'mae tem cafe buzina edition.mp3',
    'rapaz ele ta sem zap.mp3',
    'EU QUERO É SEXOW.mp3'
]



async def theTrolling_Handler():
    if random.randint(1, 50) <= 5:
        if random.randint(1, 10) <= 3:
            performAMinusculeAmountOfDespicableActions()
        else:
            theFakeout()



async def getPopulatedVc():
    servers = bot.guilds
    zap2 = None

    for index in servers:
        if index.name == "Whatsapp 2":
            zap2 = index

    VCs = zap2.voice_channels

    return [vc for vc in VCs if len(vc.voice_states) > 0]



async def theFakeout():

    Vc = getPopulatedVc()

    if len(Vc):
        Call = random.choice(Vc)

        await Call.connect()

        await asyncio.sleep(random.randint(10, 90))



async def performAMinusculeAmountOfDespicableActions():
    
    Vc = getPopulatedVc()

    if len(Vc) > 0:
        selectedCall = random.choice(Vc)
        await selectedCall.connect()

        selectedAudio = random.choice(Audios)
        source = nextcord.FFmpegPCMAudio(f"Audios/{selectedAudio}")
        botVCClient = bot.voice_clients[0]

        await asyncio.sleep(random.uniform(4, 18))

        async def stop():
            await asyncio.sleep(random.uniform(0.2, 2))  
            await botVCClient.disconnect()  

        botVCClient.play(source, after = lambda e: stop())
           


if __name__ == '__main__':
    bot.run(os.environ['DISCORD_TOKEN'])
