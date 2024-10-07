from discord.ext import commands, tasks
from discord import app_commands
from os.path import join, isdir
from random import choice
import discord, asyncio, os, utils
import tickets.utils as tutils

client = commands.Bot(command_prefix="-", sync_commands=True, intents=discord.Intents.all())
client.remove_command("help")
bot_status = discord.Status.online

@client.event
async def on_ready():
    print(f"Estou logado!\nID: {client.user.id}\nNome: {client.user}")
    await app_commands.CommandTree.sync(client.tree)
    print("Synchronized commands")
    
    lista_status = ["🛡️ Abra um ticket para retirar suas dúvidas"] 
    await client.change_presence(status=bot_status, activity=discord.Activity(type=discord.ActivityType.watching, name=choice(lista_status)))
    #changeStatus.start()

@tasks.loop(minutes=1)
async def changeStatus():
    qtd_openned = len(tutils.dbQuery("SELECT * FROM tickets_openneds"))
    qtd_closed = len(tutils.dbQuery("SELECT * FROM tickets_storage"))
    lista_status = [f"📰 Já atendemos um total de {qtd_closed} tickets.", "🛡️ Abra um ticket para retirar suas dúvidas", f"📊 Atualmente temos {qtd_openned} tickets em atendimento."] 
    await client.change_presence(status=bot_status, activity=discord.Activity(type=discord.ActivityType.watching, name=choice(lista_status)))

@client.command()
async def checknotopenneds(ctx):
	try:
		if ctx.author.id == 281495880266416139:
			r = tutils.dbQuery("SELECT CHANNEL_ID FROM tickets_openneds")
			count = 0
			for a in r:
				cn = client.get_channel(a[0])
				if cn is None:
					tutils.dbExec(f"DELETE FROM tickets_openneds WHERE CHANNEL_ID='{a[0]}'")
					count += 1		
			await ctx.reply("Success")
	except Exception as e:
		print(e)

async def main():
    async with client:
        ignoreds_cogs = ["utils"]
        onlyfolders = [f for f in os.listdir("./") if isdir(join("./", f))]
        for path in onlyfolders:
            if not path.startswith("ignore-") and path != '__pycache__':
                events = utils.getAllCogsInFolder(f"./{path}")
                for cog in events:
                    if cog not in ignoreds_cogs:
                        await utils.loadCog(client, f"{path}.{cog}", False)
        #await client.start("MTI5MTk4Nzk3OTk3MTMzNDE2Ng.GHCG0N.YRur2LM7J24Qc9KKKdoIw2-pfko_XOXgqzP4fo")
        await client.start("MTI5MjgzOTA0MTA5NTQzNDI4MA.G5pPsR.QNv8rBayvMbcOlCXi4srmyfisWzfXtUl-f5BMA")

asyncio.run(main())
