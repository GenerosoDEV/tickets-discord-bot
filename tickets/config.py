from discord.ext import commands
import discord, tickets.utils as utils
from discord import app_commands
from tickets.ticket import SelectTickets

class ConfigTicket(commands.Cog):
    def __init__(self, client):
        self.client = client

    configticket_group = app_commands.Group(name="configticket", description=f"Configuração dos tickets", guild_only=True)

    @configticket_group.command()
    async def options_add(self, inter: discord.Interaction, nome: str, descricao: str, categoria: discord.CategoryChannel, emoji_id: str=None):
        await inter.response.defer(ephemeral=True)
        if emoji_id is not None:
            if len(nome) > 25:
                await inter.followup.send(content="O nome pode ter no máximo 25 caracteres.")
                return
            elif len(descricao) > 50:
                await inter.followup.send(content="A descrição pode ter no máximo 50 caracteres.")
                return
            utils.dbExec(f"INSERT INTO ticket_options(NAME, DESCRIPTION, EMOJI_ID, CATEGORY_ID) VALUES('{nome}', '{descricao}', '{int(emoji_id)}', '{categoria.id}')")
            result = utils.dbQuery(f"SELECT * FROM tickets_panel")
            for panel in result:
                channel = self.client.get_channel(panel[0])
                await channel.purge(limit=100)
                await channel.send(embed=discord.Embed(title=panel[1], description=panel[2], color=0x11A5DC), view=SelectTickets(self.client))
        else:
            if len(nome) > 25:
                await inter.followup.send(content="O nome pode ter no máximo 25 caracteres.")
                return
            elif len(descricao) > 50:
                await inter.followup.send(content="A descrição pode ter no máximo 50 caracteres.")
                return
            utils.dbExec(f"INSERT INTO ticket_options(NAME, DESCRIPTION, CATEGORY_ID) VALUES('{nome}', '{descricao}', '{categoria.id}')")
            try:
                await self.client.get_channel(1292172843278405733).send(f"```AUTOR: {inter.user.display_name}\nID AUTOR: {inter.user.id}\nCONFIG: option_add\nOPÇÃO ADICIONADA: {nome}```")
            except Exception as e:
                print(f"CONFIG LOGS - {e}")
            await inter.followup.send(content="Opção inserida com sucesso.")
            result = utils.dbQuery(f"SELECT * FROM tickets_panel")
            for panel in result:
                channel = self.client.get_channel(panel[0])
                await channel.purge(limit=100)
                await channel.send(embed=discord.Embed(title=panel[1], description=panel[2], color=0x11A5DC), view=SelectTickets(self.client))

    @configticket_group.command()
    async def options_remove(self, inter: discord.Interaction, nome: str):
        await inter.response.defer(ephemeral=True)
        if len(nome) > 25:
            await inter.followup.send(content="O nome pode ter no máximo 25 caracteres.")
            return
        result = utils.dbQuery(f"SELECT * FROM ticket_options WHERE NAME='{nome}'")
        if result is not None:
            utils.dbExec(f"DELETE FROM ticket_options WHERE NAME='{nome}'")
            try:
                await self.client.get_channel(1292172843278405733).send(f"```AUTOR: {inter.user.display_name}\nID AUTOR: {inter.user.id}\nCONFIG: option_remove\nOPÇÃO REMOVIDA: {nome}```")
            except Exception as e:
                print(f"CONFIG LOGS - {e}")
            await inter.followup.send(content="Opção removida.")
            result = utils.dbQuery(f"SELECT * FROM tickets_panel")
            for panel in result:
                channel = self.client.get_channel(panel[0])
                await channel.purge(limit=100)
                await channel.send(embed=discord.Embed(title=panel[1], description=panel[2], color=0x11A5DC), view=SelectTickets(self.client))
        else:
            await inter.followup.send(content="Essa opção não existe.")

    @configticket_group.command()
    async def panel(self, inter: discord.Interaction, titulo_embed:str, descricao_embed:str, canal: discord.TextChannel):
        await inter.response.defer(ephemeral=True)
        if len(titulo_embed) > 256:
            await inter.followup.send(content="O título pode ter no máximo 256 caracteres.")
            return
        if len(descricao_embed) > 4096:
            await inter.followup.send(content="A descrição pode ter no máximo 4096 caracteres.")
            return
        result = utils.dbQuery(f"SELECT * FROM tickets_panel")
        if result is not None:
            for panel in result:
                channel = self.client.get_channel(panel[0])
                await channel.purge(limit=100)
        utils.dbExec(f"DELETE FROM tickets_panel")
        utils.dbExec(f"INSERT INTO tickets_panel(CHANNEL_SEND_ID, TITLE, DESCRIPTION) VALUES('{canal.id}', '{titulo_embed}', '{descricao_embed}')")
        try:
            await self.client.get_channel(1292172843278405733).send(f"```AUTOR: {inter.user.display_name}\nID AUTOR: {inter.user.id}\nCONFIG: panel\nNOVO CANAL: {canal.id}\nTÍTULO EMBED: {titulo_embed}\nDESCRIÇÃO EMBED: {descricao_embed}```")
        except Exception as e:
            print(f"CONFIG LOGS - {e}")
        await canal.purge(limit=100)
        embed = discord.Embed(title=titulo_embed, description=descricao_embed, color=0x11A5DC)
        embed.set_thumbnail(url=self.client.user.avatar)
        await canal.send(embed=embed, view=SelectTickets(self.client))
        await inter.followup.send("Ticket panel configurado com sucesso!")

    @configticket_group.command()
    async def snippet_add(self, inter: discord.Interaction, nome: str, texto: str):
        await inter.response.defer(ephemeral=True)
        if len(nome) > 30:
            await inter.followup.send("O nome pode ter no máximo 30 caracteres.")
            return
        if len(texto) > 1500:
            await inter.followup.send("O texto pode ter no máximo 1500 caracteres.")
            return
        utils.dbExec(f"INSERT INTO tickets_snippets(SNIPPET_NAME, SNIPPET_TEXT) VALUES('{nome}', '{texto}')")
        try:
            await self.client.get_channel(1292172843278405733).send(f"```AUTOR: {inter.user.display_name}\nID AUTOR: {inter.user.id}\nCONFIG: snippet_add\nSNIPPET ADICIONADO: {nome}```")
        except Exception as e:
            print(f"CONFIG LOGS - {e}")
        await inter.followup.send("Snippet adicionado com sucesso.")

    @configticket_group.command()
    async def snippet_remove(self, inter: discord.Interaction, nome: str):
        await inter.response.defer(ephemeral=True)
        if len(nome) > 30:
            await inter.followup.send("O nome pode ter no máximo 30 caracteres.")
            return
        result = utils.dbQuery(f"SELECT * FROM tickets_snippets WHERE SNIPPET_NAME='{nome}'")
        if result is not None:
            utils.dbExec(f"DELETE FROM tickets_snippets WHERE SNIPPET_NAME='{nome}'")
            try:
                await self.client.get_channel(1292172843278405733).send(f"```AUTOR: {inter.user.display_name}\nID AUTOR: {inter.user.id}\nCONFIG: snippet_remove\nSNIPPET REMOVIDO: {nome}```")
            except Exception as e:
                print(f"CONFIG LOGS - {e}")
            await inter.followup.send("Snippet removido com sucesso.")
        else:
            await inter.followup.send("Esse snippet não existe.")

    @configticket_group.command()
    async def prefix_add(self, inter: discord.Interaction, cargo: discord.Role, prefixo: str):
        await inter.response.defer(ephemeral=True)
        if len(prefixo) > 150:
            await inter.followup.send("O prefixo pode ter no máximo 150 caracteres.")
            return
        utils.dbExec(f"INSERT INTO tickets_prefixes(ROLE_ID, PREFIX) VALUES('{cargo.id}', '{prefixo}')")
        try:
            await self.client.get_channel(1292172843278405733).send(f"```AUTOR: {inter.user.display_name}\nID AUTOR: {inter.user.id}\nCONFIG: prefix_add\nCARGO ADICIONADO: {cargo.id}\nPREFIXO: {prefixo}```")
        except Exception as e:
            print(f"CONFIG LOGS - {e}")
        await inter.followup.send("Prefixo adicionado com sucesso.")
        
    @configticket_group.command()
    async def prefix_remove(self, inter: discord.Interaction, cargo: discord.Role):
        await inter.response.defer(ephemeral=True)
        result = utils.dbQuery(f"SELECT * FROM tickets_prefixes WHERE ROLE_ID='{cargo.id}'")
        if result is not None:
            utils.dbExec(f"DELETE FROM tickets_prefixes WHERE ROLE_ID='{cargo.id}'")
            try:
                await self.client.get_channel(1292172843278405733).send(f"```AUTOR: {inter.user.display_name}\nID AUTOR: {inter.user.id}\nCONFIG: prefix_remove\nCARGO REMOVIDO: {cargo.id}```")
            except Exception as e:
                print(f"CONFIG LOGS - {e}")
            await inter.followup.send("Prefixo removido com sucesso.")
        else:
            await inter.followup.send("Esse prefixo não existe.")
            
        

async def setup(client):
    await client.add_cog(ConfigTicket(client))
    