from discord.ext import commands
import datetime
import discord
from .utils import db
import time

class settings_table(db.Table, table_name='settings'):
    id = db.Column(db.Integer(big=True), primary_key=True)
    logging_enabled = db.Column(db.Boolean, default=False)
    logging_channel = db.Column(db.Integer(big=True))

class Settings():
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        if not ctx.invoked_subcommand:
            
            embed = discord.Embed(color=discord.Color.dark_teal(), title='Settings', description='Configure this server\'s settings.')
            embed.add_field(name="Logging", value="Sets up logging for the major things that can happen in the server.\n``settings logging enable <module>`` | ``settings logging enable <module>``", inline=True)
            embed.add_field(name="Prefix", value="Configrues the prefix for this server.\n``settings prefix add <prefix>`` | ``settings prefix remove <prefix>``\nPut the prefix in \"quotes\" to make it have spaces.", inline=True)
            embed.add_field(name="Starboard", value="Sets up a starboard.\n``starboard [name of the starboard channel]``")
            embed.set_footer(text="For more information search across the help menu.")
            embed.timestamp = datetime.datetime.utcnow()

            await ctx.send(embed=embed)

    @settings.group()
    async def logging(self, ctx):
        pass

    @logging.group()
    async def enable(self, ctx):
        # if args is None:
        #     return await ctx.send('Valid settings for logging ``message_edit``, ``message_delete``, ``join``, ``leave``, ``kick``, ``ban``, ``command``')
        print('lol')
    
    @enable.command(name='message_edit')
    async def _message_edit(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set message_edit=true where id={ctx.guild.id}')
            return await ctx.send('Message edit logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, message_edit) values ({ctx.guild.id}, true)')
            return await ctx.send('Message edit logging is now enabled.')

    @enable.command()
    async def message_delete(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set message_delete=true where id={ctx.guild.id}')
            return await ctx.send('Message delete logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, mesage_delete) values ({ctx.guild.id}, true)')
            return await ctx.send('Message delete logging is now enabled.')

    @enable.command()
    async def join(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set join=true where id={ctx.guild.id}')
            return await ctx.send('Join logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, join) values ({ctx.guild.id}, true)')
            return await ctx.send('Join logging is now enabled.')

    @enable.command()
    async def leave(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set leave=true where id={ctx.guild.id}')
            return await ctx.send('Leave logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, leave) values ({ctx.guild.id}, true)')
            return await ctx.send('Leave logging is now enabled.')

    @enable.command()
    async def kick(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set kick=true where id={ctx.guild.id}')
            return await ctx.send('Kick logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, kick) values ({ctx.guild.id}, true)')
            return await ctx.send('Kick logging is now enabled.')

    @enable.command()
    async def ban(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set ban=true where id={ctx.guild.id}')
            return await ctx.send('Ban logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, ban) values ({ctx.guild.id}, true)')
            return await ctx.send('Ban logging is now enabled.')

    @enable.command()
    async def commands(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set log_commands=true where id={ctx.guild.id}')
            return await ctx.send('Command logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, log_commands) values ({ctx.guild.id}, true)')
            return await ctx.send('Command logging is now enabled.')

    @logging.group()
    async def disable(self, ctx):
        cmd = self.bot.get_command('disablelogging')
        await ctx.invoke(cmd)

    @disable.command(name='message_edit')
    async def _message_edit(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set message_edit=true where id={ctx.guild.id}')
            return await ctx.send('Message edit logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, message_edit) values ({ctx.guild.id}, true)')
            return await ctx.send('Message edit logging is now enabled.')

    @disable.command(name="message_delete")
    async def _message_delete(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set message_delete=true where id={ctx.guild.id}')
            return await ctx.send('Message delete logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, mesage_delete) values ({ctx.guild.id}, true)')
            return await ctx.send('Message delete logging is now enabled.')

    @disable.command(name="join")
    async def join(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set join=true where id={ctx.guild.id}')
            return await ctx.send('Join logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, join) values ({ctx.guild.id}, true)')
            return await ctx.send('Join logging is now enabled.')

    @disable.command(name="leave")
    async def leave(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set leave=true where id={ctx.guild.id}')
            return await ctx.send('Leave logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, leave) values ({ctx.guild.id}, true)')
            return await ctx.send('Leave logging is now enabled.')

    @disable.command(name="kick")
    async def kick(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set kick=true where id={ctx.guild.id}')
            return await ctx.send('Kick logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, kick) values ({ctx.guild.id}, true)')
            return await ctx.send('Kick logging is now enabled.')

    @disable.command(name="ban")
    async def ban(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set ban=true where id={ctx.guild.id}')
            return await ctx.send('Ban logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, ban) values ({ctx.guild.id}, true)')
            return await ctx.send('Ban logging is now enabled.')

    @disable.command(name="commands")
    async def _commands(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data[0]:
            await self.bot.pool.execute(f'update settings set commands=true where id={ctx.guild.id}')
            return await ctx.send('Command logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, commands) values ({ctx.guild.id}, true)')
            return await ctx.send('Command logging is now enabled.')

    @settings.group()
    async def prefix(self, ctx):
        if not ctx.invoked_subcommand:
            cmd = self.bot.get_command('prefix')
            await ctx.invoke(cmd)

    @prefix.command()
    async def add(self, ctx, *, prefix: str):
        prefix = prefix.strip("\"")
        cmd = self.bot.get_command('prefix add')
        await ctx.invoke(cmd, prefix=prefix)

    @prefix.command()
    async def remove(self, ctx, *, prefix: str):
        prefix = prefix.strip("\"")
        cmd = self.bot.get_command('prefix remove')
        await ctx.invoke(cmd, prefix=prefix)
    
    @settings.command()
    async def starboard(self, ctx, *, name='starboard'):
        cmd = self.bot.get_command('starboard')
        await ctx.invoke(cmd, name=name)

    # @commands.command(hidden=True)
    # async def realping(self, ctx):
    #     before = time.monotonic()
    #     message = await ctx.send("Pong")
    #     ping = (time.monotonic() - before) * 1000
    #     await message.edit(content=f"My ping\nMSG :: {int(ping)}ms\nAPI :: {round(self.bot.latency * 1000)}ms")

def setup(bot):
    bot.add_cog(Settings(bot))
