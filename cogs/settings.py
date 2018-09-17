from discord.ext import commands
from .utils import checks
import datetime
import discord
import time

class Settings():
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group()
    @checks.has_permissions(administrator=True)
    async def settings(self, ctx):
        if not ctx.invoked_subcommand:
            
            embed = discord.Embed(color=discord.Color.dark_teal(), title='Settings', description='Configure this server\'s settings.')
            embed.add_field(name="Logging", value="Sets up logging for the major things that can happen in the server.\n``settings logging <enable|disable> <module>``\nValid modules are: ``kick``, ``ban``, ``join``, ``leave``, ``commands``, ``message_edit``, ``message_delete``", inline=True)
            embed.add_field(name="Prefix", value="Configrues the prefix for this server.\n``settings prefix <add|remove> <prefix>``\nPut the prefix in \"quotes\" to make it have spaces.", inline=True)
            embed.add_field(name="Starboard", value="Sets up a starboard.\n``starboard [name of the starboard channel]``")
            embed.add_field(name="Buy roles", value="Sets up a role buying.\n``settings buy_roles <enable|disable>``")
            embed.add_field(name="Anti advertising", value="Sets up anti advertising\n``settings antiadvert <enable|disable>``")
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
        pass

    @settings.group(name='buy_roles')
    async def _buy_roles(self, ctx):
        pass

    @_buy_roles.command(name='enable')
    async def __enable(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set buy_roles=true where id={ctx.guild.id}')
            return await ctx.send('Role buying is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, buy_roles) values ({ctx.guild.id}, true)')
            return await ctx.send('Role buying is now enabled.')

    @_buy_roles.command(name='disable')
    async def __disable(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set buy_roles=false where id={ctx.guild.id}')
            return await ctx.send('Role buying is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, buy_roles) values ({ctx.guild.id}, false)')
            return await ctx.send('Role buying is now enabled.')

    @settings.group()
    async def antiadvert(self, ctx):
        pass

    @antiadvert.command(name='enable')
    async def anti_enable(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set advert=true where id={ctx.guild.id}')
            return await ctx.send('Anti advertising is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, advert) values ({ctx.guild.id}, true)')
            return await ctx.send('Anti advertising is now enabled.')

    @antiadvert.command(name='disable')
    async def anti_disable(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set advert=false where id={ctx.guild.id}')
            return await ctx.send('Anti advertising is now disabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, advert) values ({ctx.guild.id}, false)')
            return await ctx.send('Anti advertising is now disabled.')


    @enable.command(name='message_edit')
    async def _message_edit(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set message_edit=true where id={ctx.guild.id}')
            return await ctx.send('Message edit logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, message_edit) values ({ctx.guild.id}, true)')
            return await ctx.send('Message edit logging is now enabled.')

    @enable.command()
    async def message_delete(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set message_delete=true where id={ctx.guild.id}')
            return await ctx.send('Message delete logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, message_delete) values ({ctx.guild.id}, true)')
            return await ctx.send('Message delete logging is now enabled.')

    @enable.command()
    async def join(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set log_join=true where id={ctx.guild.id}')
            return await ctx.send('Join logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, log_join) values ({ctx.guild.id}, true)')
            return await ctx.send('Join logging is now enabled.')

    @enable.command()
    async def leave(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set leave=true where id={ctx.guild.id}')
            return await ctx.send('Leave logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, leave) values ({ctx.guild.id}, true)')
            return await ctx.send('Leave logging is now enabled.')

    @enable.command()
    async def kick(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set kick=true where id={ctx.guild.id}')
            return await ctx.send('Kick logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, kick) values ({ctx.guild.id}, true)')
            return await ctx.send('Kick logging is now enabled.')

    @enable.command()
    async def ban(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set ban=true where id={ctx.guild.id}')
            return await ctx.send('Ban logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, ban) values ({ctx.guild.id}, true)')
            return await ctx.send('Ban logging is now enabled.')

    @enable.command()
    async def commands(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set log_commands=true where id={ctx.guild.id}')
            return await ctx.send('Command logging is now enabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, log_commands) values ({ctx.guild.id}, true)')
            return await ctx.send('Command logging is now enabled.')

    @logging.group()
    async def disable(self, ctx):
        pass

    @disable.command(name='message_edit')
    async def _message_edit(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set message_edit=false where id={ctx.guild.id}')
            return await ctx.send('Message edit logging is now disabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, message_edit) values ({ctx.guild.id}, false)')
            return await ctx.send('Message edit logging is now disabled.')

    @disable.command(name="message_delete")
    async def _message_delete(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set message_delete=false where id={ctx.guild.id}')
            return await ctx.send('Message delete logging is now disabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, message_delete) values ({ctx.guild.id}, false)')
            return await ctx.send('Message delete logging is now disabled.')

    @disable.command(name="join")
    async def _join(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set log_join=false where id={ctx.guild.id}')
            return await ctx.send('Join logging is now disabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, join) values ({ctx.guild.id}, false)')
            return await ctx.send('Join logging is now disabled.')

    @disable.command(name="leave")
    async def _leave(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set leave=false where id={ctx.guild.id}')
            return await ctx.send('Leave logging is now disabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, leave) values ({ctx.guild.id}, false)')
            return await ctx.send('Leave logging is now disabled.')

    @disable.command(name="kick")
    async def _kick(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set kick=false where id={ctx.guild.id}')
            return await ctx.send('Kick logging is now disabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, kick) values ({ctx.guild.id}, false)')
            return await ctx.send('Kick logging is now disabled.')

    @disable.command(name="ban")
    async def _ban(self, ctx):
        data = await self.bot.pool.fetchrow(f'select id from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set ban=false where id={ctx.guild.id}')
            return await ctx.send('Ban logging is now disabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, ban) values ({ctx.guild.id}, false)')
            return await ctx.send('Ban logging is now disabled.')

    @disable.command(name="commands")
    async def _commands(self, ctx):
        data = await self.bot.pool.fetchrow(f'select * from settings where id={ctx.guild.id}')
        if data:
            await self.bot.pool.execute(f'update settings set log_commands=false where id={ctx.guild.id}')
            return await ctx.send('Command logging is now disabled.')
        else:
            await self.bot.pool.execute(f'insert into settings (id, log_commands) values ({ctx.guild.id}, false)')
            return await ctx.send('Command logging is now disabled.')

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

    async def on_message(self, message):
        if message.author.bot: return
        data = await self.bot.pool.fetchrow(f'select advert from settings where id={message.guild.id}')
        if not data: return
        if not data[0]: return
        ctx = await self.bot.get_context(message)
        resolved = ctx.author.guild_permissions
        if getattr(resolved, 'manage_messages', None) == True: return
        if 'https://discord.gg/' in message.content:
            try:
                await message.delete()
                await message.channel.send('Don\'t advertise here dude.', delete_after=10)
                try:
                    send_channel = discord.utils.get(message.guild.text_channels, name='W.Bot-logging')
                    await send_channel.send(f'{message.author.display_name} was advertising in {message.channel.mention} message content was:\n{message.clean_content}')
                except:
                    return
            except discord.Forbidden:
                pass
        elif 'discord.gg/' in message.content:
            try:
                await message.delete()
                await message.channel.send('Don\'t advertise here dude.', delete_after=10)
                try:
                    send_channel = discord.utils.get(message.guild.text_channels, name='W.Bot-logging')
                    await send_channel.send(f'{message.author.display_name} was advertising in {message.channel.mention} message content was:\n{message.clean_content}')
                except:
                    return
            except discord.Forbidden:
                pass

def setup(bot):
    bot.add_cog(Settings(bot))
