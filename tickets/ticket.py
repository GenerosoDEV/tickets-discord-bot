from unidecode import unidecode
from discord.ext import commands
import discord, tickets.utils as utils, asyncio, os
from discord import app_commands

class Ticket(commands.Cog):
    def __init__(self, client):
        self.client = client
        utils.dbExec("""CREATE TABLE IF NOT EXISTS ticket_options (NAME TEXT, DESCRIPTION TEXT, EMOJI_ID BIGINT, CATEGORY_ID BIGINT);""")
        utils.dbExec("""CREATE TABLE IF NOT EXISTS tickets_panel (CHANNEL_SEND_ID BIGINT, TITLE TEXT, DESCRIPTION TEXT);""")
        utils.dbExec("""CREATE TABLE IF NOT EXISTS tickets_snippets (SNIPPET_NAME TEXT, SNIPPET_TEXT TEXT);""")
        utils.dbExec("""CREATE TABLE IF NOT EXISTS tickets_openneds (OWNER_TICKET_UID BIGINT, CHANNEL_ID BIGINT, MESSAGES TEXT, ATENDANTS TEXT);""")
        utils.dbExec("""CREATE TABLE IF NOT EXISTS tickets_storage (PROTOCOL_UID INTEGER PRIMARY KEY AUTOINCREMENT, OWNER_TICKET_UID BIGINT, MESSAGES TEXT, ATENDANTS TEXT);""")
        utils.dbExec("""CREATE TABLE IF NOT EXISTS tickets_prefixes (ROLE_ID BIGINT, PREFIX TEXT);""")
        

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            result = utils.dbQuery(f"SELECT * FROM tickets_panel")
            for panel in result:
                channel = self.client.get_channel(panel[0])
                await channel.purge(limit=100)
                await channel.send(f"Me envie uma mensagem na DM para abrir um ticket! ({self.client.user.mention})")
                #embed = discord.Embed(title=panel[1], description=panel[2], color=0x11A5DC)
                #embed.set_thumbnail(url=self.client.user.avatar)
                #await channel.send(embed=embed, view=SelectTickets(self.client))
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.channel.DMChannel):
            result = utils.dbQuery(f"SELECT * FROM tickets_openneds WHERE OWNER_TICKET_UID='{message.author.id}'")
            if result is not None:
                channel_id = result[0][1]
                attachs = ""
                if message.attachments != []:
                    for attach in message.attachments:
                        attachs = f"{attachs}\n{attach.url}".strip("\n")

                user_name = f"{message.author.name}#{message.author.discriminator}".replace("'", "")
                if attachs != "":
                    utils.dbExec(f"UPDATE tickets_openneds SET MESSAGES='{result[0][2]}{user_name}: {message.content} | \nAttachments: {attachs}-_SEPARATOR_-' WHERE OWNER_TICKET_UID='{message.author.id}'")
                    await self.client.get_channel(channel_id).send(f"**{user_name}: **{message.content} \n\n`Attachments:` {attachs}")
                else:
                    utils.dbExec(f"UPDATE tickets_openneds SET MESSAGES='{result[0][2]}{user_name}: {message.content}-_SEPARATOR_-' WHERE OWNER_TICKET_UID='{message.author.id}'")
                    await self.client.get_channel(channel_id).send(f"**{user_name}: **{message.content}")

                await message.add_reaction("✅")
            else:
                result = utils.dbQuery(f"SELECT * FROM tickets_panel")
                for panel in result:
                    embed = discord.Embed(title=panel[1], description=panel[2], color=0x11A5DC)
                    embed.set_thumbnail(url=self.client.user.avatar)
                    await message.author.send(content="Olá! Você não tem um ticket aberto!\n", embed=embed, view=SelectTickets(self.client))

        else:
            if message.content.startswith("---"): # SNIPPET NORMAL
                result = utils.dbQuery(f"SELECT * FROM tickets_openneds WHERE CHANNEL_ID='{message.channel.id}'")
                if result is not None:
                    name = message.content.split()[0][3:]
                    if name != "":
                        result_snippet = utils.dbQuery(f"SELECT SNIPPET_TEXT FROM tickets_snippets WHERE SNIPPET_NAME='{name}'")
                        if result_snippet is not None:
                            user = self.client.get_user(result[0][0])
                            snippet_text = result_snippet[0][0]
                            roles = message.author.roles
                            roles.reverse()
                            prefix = ""
                            for role in roles:
                                result_prefix = utils.dbQuery(f"SELECT PREFIX FROM tickets_prefixes WHERE ROLE_ID='{role.id}'")
                                if result_prefix is not None:
                                    prefix = result_prefix[0][0]
                            user_name = f"{message.author.display_name}".replace("'", "")
                            utils.dbExec(f"UPDATE tickets_openneds SET MESSAGES='{result[0][2]}{user_name}: {snippet_text}-_SEPARATOR_-' WHERE OWNER_TICKET_UID='{message.author.id}'")
                            await message.delete()
                            await user.send(f"**{prefix} - {user_name}: **{snippet_text}")
                            await message.channel.send(f"**{prefix} - {user_name}: **{snippet_text}")
                        else:
                            await message.reply("Esse snippet não existe.")
            elif message.content.startswith("--"): # SNIPPET ANON
                result = utils.dbQuery(f"SELECT * FROM tickets_openneds WHERE CHANNEL_ID='{message.channel.id}'")
                if result is not None:
                    name = message.content.split()[0][2:]
                    if name != "":
                        result_snippet = utils.dbQuery(f"SELECT SNIPPET_TEXT FROM tickets_snippets WHERE SNIPPET_NAME='{name}'")
                        if result_snippet is not None:
                            user = self.client.get_user(result[0][0])
                            snippet_text = result_snippet[0][0]
                            roles = message.author.roles
                            roles.reverse()
                            prefix = ""
                            for role in roles:
                                result_prefix = utils.dbQuery(f"SELECT PREFIX FROM tickets_prefixes WHERE ROLE_ID='{role.id}'")
                                if result_prefix is not None:
                                    prefix = result_prefix[0][0]
                            user_name = f"{message.author.display_name}".replace("'", "")
                            utils.dbExec(f"UPDATE tickets_openneds SET MESSAGES='{result[0][2]}(Anônimo) {user_name}: {snippet_text}-_SEPARATOR_-' WHERE OWNER_TICKET_UID='{message.author.id}'")
                            await message.delete()
                            await user.send(f"**{prefix}: **{snippet_text}")
                            await message.channel.send(f"*(Anônimo)* **{prefix} - {user_name}:** {snippet_text}")
                        else:
                            await message.reply("Esse snippet não existe.")

    @commands.command(aliases=["responder", "response"])
    async def r(self, ctx):
        result = utils.dbQuery(f"SELECT OWNER_TICKET_UID, MESSAGES, ATENDANTS FROM tickets_openneds WHERE CHANNEL_ID='{ctx.channel.id}'")
        if result is not None:
            user = self.client.get_user(result[0][0])
            message = ctx.message
            command = ctx.message.content.split()[0]
            messagecontent = ctx.message.content.replace(command, "")
            roles = ctx.author.roles
            roles.reverse()
            prefix = ""
            for role in roles:
                result_prefix = utils.dbQuery(f"SELECT PREFIX FROM tickets_prefixes WHERE ROLE_ID='{role.id}'")
                if result_prefix is not None:
                    prefix = result_prefix[0][0]
            attachs = ""
            if message.attachments != []:
                for attach in message.attachments:
                    attachs = f"{attachs}\n{attach.url}".strip("\n")

            user_name = f"{ctx.author.display_name}".replace("'", "")
            if attachs != "":
                utils.dbExec(f"UPDATE tickets_openneds SET MESSAGES='{result[0][1]}{user_name}: {messagecontent} | Attachments: {attachs}-_SEPARATOR_-' WHERE OWNER_TICKET_UID='{user.id}'")
                await ctx.message.delete()
                await user.send(f"**{prefix} - {user_name}: **{messagecontent} \n\n`Attachments:` {attachs}")
                await ctx.send(f"**{prefix} - {user_name}: **{messagecontent} \n\n`Attachments:` {attachs}")
            else:
                utils.dbExec(f"UPDATE tickets_openneds SET MESSAGES='{result[0][1]}{user_name}: {messagecontent}-_SEPARATOR_-' WHERE OWNER_TICKET_UID='{user.id}'")
                await ctx.message.delete()
                await user.send(f"**{prefix} - {user_name}: **{messagecontent}")
                await ctx.send(f"**{prefix} - {user_name}: **{messagecontent}")

            if str(ctx.author.id) not in result[0][2].split():
                utils.dbExec(f"UPDATE tickets_openneds SET ATENDANTS='{result[0][2]} {ctx.author.id}' WHERE OWNER_TICKET_UID='{result[0][0]}'")

    @commands.command(aliases=["anonymousresponse", "ra", "responderanonimo"])
    async def ar(self, ctx):
        result = utils.dbQuery(f"SELECT OWNER_TICKET_UID, MESSAGES, ATENDANTS FROM tickets_openneds WHERE CHANNEL_ID='{ctx.channel.id}'")
        if result is not None:
            user = self.client.get_user(result[0][0])
            message = ctx.message
            command = ctx.message.content.split()[0]
            messagecontent = ctx.message.content.replace(command, "")
            roles = ctx.author.roles
            roles.reverse()
            prefix = ""
            for role in roles:
                result_prefix = utils.dbQuery(f"SELECT PREFIX FROM tickets_prefixes WHERE ROLE_ID='{role.id}'")
                if result_prefix is not None:
                    prefix = result_prefix[0][0]
            attachs = ""
            if message.attachments != []:
                for attach in message.attachments:
                    attachs = f"{attachs}\n{attach.url}".strip("\n")
            user_name = f"{ctx.author.display_name}".replace("'", "")
            if attachs != "":
                utils.dbExec(f"UPDATE tickets_openneds SET MESSAGES='{result[0][1]}(Anônimo) {user_name}: {messagecontent} | Attachments: {attachs}-_SEPARATOR_-' WHERE OWNER_TICKET_UID='{user.id}'")
                await ctx.message.delete()
                await user.send(f"**{prefix}:**{messagecontent} \n\n`Attachments:` {attachs}")
                await ctx.send(f"*(Anônimo)* **{prefix} - {user_name}:**{messagecontent} \n\n`Attachments:` {attachs}")
            else:
                utils.dbExec(f"UPDATE tickets_openneds SET MESSAGES='{result[0][1]}(Anônimo) {user_name}: {messagecontent}-_SEPARATOR_-' WHERE OWNER_TICKET_UID='{user.id}'")
                await ctx.message.delete()
                await user.send(f"**{prefix}:**{messagecontent}")
                await ctx.send(f"*(Anônimo)* **{prefix} - {user_name}:**{messagecontent}")

            if str(ctx.author.id) not in result[0][2].split():
                utils.dbExec(f"UPDATE tickets_openneds SET ATENDANTS='{result[0][2]} {ctx.author.id}' WHERE OWNER_TICKET_UID='{result[0][0]}'")

    @commands.command(aliases=["fechar"])
    async def close(self, ctx, *, last_message=None):
        result = utils.dbQuery(f"SELECT * FROM tickets_openneds WHERE CHANNEL_ID='{ctx.channel.id}'")
        if result is not None:
            await ctx.reply("Ticket sendo fechado em 10 segundos.")
            await asyncio.sleep(10)
            user = self.client.get_user(result[0][0])
            channel = self.client.get_channel(result[0][1])
            await channel.delete()
            utils.dbExec(f"INSERT INTO tickets_storage(OWNER_TICKET_UID, MESSAGES, ATENDANTS) VALUES('{result[0][0]}', '{result[0][2]}', '{result[0][3]}')")
            utils.dbExec(f"DELETE FROM tickets_openneds WHERE OWNER_TICKET_UID='{user.id}'")
            result_tickets_storage = utils.dbQuery(f"SELECT PROTOCOL_UID FROM tickets_storage ORDER BY PROTOCOL_UID DESC")
            protocol_uid = result_tickets_storage[0][0]
            if last_message is not None:
                try:
                    await user.send(embed=discord.Embed(title="Ticket fechado!", description=last_message, color=0x11A5DC).set_footer(text=f"Protocolo: {protocol_uid}"))
                except:
                    pass
                try:
                    await ctx.author.send(embed=discord.Embed(title=f"Você fechou o ticket de {user}!", description=last_message, color=0x11A5DC).set_footer(text=f"Protocolo: {protocol_uid}"))
                except:
                    pass
                await self.client.get_channel(1293536859867320340).send(f"```STAFF: {ctx.author.display_name}\nID STAFF: {ctx.author.id}\nMENSAGEM DE FECHAMENTO: {last_message}\nPROTOCOLO: {protocol_uid}```")
            else:
                try: 
                    await user.send(embed=discord.Embed(title="Ticket fechado!", color=0x11A5DC).set_footer(text=f"Protocolo: {protocol_uid}"))
                except:
                    pass
                try:
                    await ctx.author.send(embed=discord.Embed(title=f"Você fechou o ticket de {user}!", color=0x11A5DC).set_footer(text=f"Protocolo: {protocol_uid}"))
                except:
                    pass
                await self.client.get_channel(1293536859867320340).send(f"```STAFF: {ctx.author.display_name}\nID STAFF: {ctx.author.id}\nPROTOCOLO: {protocol_uid}```")

    @app_commands.command(description=f"Cheque a lista de snippets ou um snippet específico")
    @app_commands.guild_only()
    @app_commands.describe(nome_snippet="Nome do snippet que você deseja checar.")
    async def snippet(self, inter: discord.Interaction, nome_snippet: str=None):
        if nome_snippet is None:
            result = utils.dbQuery(f"SELECT SNIPPET_NAME FROM tickets_snippets")
            list_snippets = ""
            for snippet in result:
                list_snippets = f"{list_snippets}{snippet[0]}, "
            list_snippets = list_snippets.strip(", ")
            await inter.response.send_message(ephemeral=True, content=f"Lista de Snippets: \n```{list_snippets}```")

        else:
            result = utils.dbQuery(f"SELECT SNIPPET_TEXT FROM tickets_snippets WHERE SNIPPET_NAME='{nome_snippet}'")
            if result is not None:
                await inter.response.send_message(ephemeral=True, content=f"Texto do snippet `{nome_snippet}`: \n```{result[0][0]}```")
            else: 
                await inter.response.send_message(ephemeral=True, content="Esse snippet não existe.")


    @app_commands.command(description=f"Cheque as informações de um ticket já fechado.")
    @app_commands.guild_only()
    @app_commands.describe(protocolo="Protocolo do ticket que você deseja ver as informações.")
    async def transcript(self, inter: discord.Interaction, protocolo: int):
        await inter.response.defer(ephemeral=True)
        try:
            result = utils.dbQuery(f"SELECT * FROM tickets_storage WHERE PROTOCOL_UID='{protocolo}'")
            if result is not None:
                result = result[0]
                atendants_ids = result[3].strip().replace(' ', ', ').strip(', ')
                history_messages = result[2].replace('-_SEPARATOR_-', '\n')
                with open(f"./tickets/transcript_{protocolo}.txt", 'w') as f:
                    history_messages = u''+history_messages
                    undecoded_history_messages = unidecode(history_messages)
                    f.write(undecoded_history_messages)

                await inter.followup.send(ephemeral=True, content=f"ID do Usuário que abriu o ticket: {result[1]}\nID dos atendentes: {atendants_ids}", file=discord.File(f"./tickets/transcript_{protocolo}.txt"))
                os.remove(f"./tickets/transcript_{protocolo}.txt")
                await self.client.get_channel(1293536859867320340).send(f"{inter.user.display_name} ({inter.user.id}) utilizou `/transcript` no protocolo `{protocolo}`")
            else:
                await inter.followup.send(f"Nenhum ticket registrado nesse protocolo.", ephemeral=True)
        except Exception as e: 
            print(e)

class ModalOpenTicket(discord.ui.Modal):
    def __init__(self, client, category_id, creator_id):
        super().__init__(title="Abrindo seu ticket")
        self.client = client
        self.category_id = category_id
        self.creator_id = creator_id
        self.uid = discord.ui.TextInput(label="Informe seu ID in-game (se tiver)", required=True, max_length=5)
        self.reason = discord.ui.TextInput(label="Conte-nos sobre o que você precisa", required=True, max_length=1000)
        self.add_item(self.uid)
        self.add_item(self.reason)

    async def on_submit(self, inter: discord.Interaction):
        try:    
            await inter.response.defer(ephemeral=False)
            category = self.client.get_channel(self.category_id)
            text_channel_name = f"{inter.user.name}"
            text_channel_name = u''+text_channel_name
            undecoded_text_channel_name = unidecode(text_channel_name)
            channel = await category.guild.create_text_channel(f"{undecoded_text_channel_name}", category=category)
            await channel.edit(sync_permissions=True)
            user_name = f"{inter.user.name}".replace("'", "")
            utils.dbExec(f"INSERT INTO tickets_openneds(OWNER_TICKET_UID, CHANNEL_ID, MESSAGES, ATENDANTS) VALUES('{inter.user.id}', '{channel.id}', '{user_name}: {self.reason}-_SEPARATOR_-', '')")
            await channel.send(f"{inter.user.mention} - `{inter.user.name}` (`{inter.user.id}`) \n**ID In-Game: **{self.uid}\n**Sobre:** {self.reason}")
            await inter.followup.send(embed=discord.Embed(color=0x11A5DC, title="Ticket aberto!", description="Aguarde uma resposta!"), ephemeral=False)
            
        except Exception as e:
            print("Erro ao abrir ticket: " + str(e))

class SelectTickets(discord.ui.View):
    def __init__(self, client):
        super().__init__(timeout=None)
        self.client = client

        result = utils.dbQuery(f"SELECT * FROM ticket_options")
        self.result = result
        for option in result:
            if option[2] is not None and option[2] != "":
                emoji = self.client.get_emoji(option[2])
                if emoji is not None:
                    self.ticket.add_option(label=option[0], description=option[1], emoji=emoji, value=option[3])
                else:
                    try:
                        self.ticket.add_option(label=option[0], description=option[1], emoji=option[2], value=option[3])
                    except:
                        self.ticket.add_option(label=option[0], description=option[1], value=option[3])  
            else:
                self.ticket.add_option(label=option[0], description=option[1], value=option[3])

    @discord.ui.select(placeholder="Aperte aqui para abrir um ticket", min_values=0, max_values=1)
    async def ticket(self,inter:discord.Interaction,select:discord.ui.select):
        if len(inter.data["values"]) > 0:
            if utils.dbQuery(f"SELECT * FROM tickets_openneds WHERE OWNER_TICKET_UID='{inter.user.id}'") is None:
                await inter.response.send_modal(ModalOpenTicket(self.client, int(inter.data["values"][0]), inter.user.id))
            else:
                await inter.response.send_message(f"Você já tem um ticket aberto!", ephemeral=True)
        else:
            await inter.response.defer(ephemeral=True)


async def setup(client):
    await client.add_cog(Ticket(client))
    
