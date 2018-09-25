from discord.ext import commands
from .utils import checks
import datetime
import discord
import time

class SettingsConfig:
    def __init__(self, bot, record):
        self.bot = bot
        self.id = record['id']
        self.message_delete = record['message_delete'] or False
        self.message_edit = record['message_edit'] or False
        self.join = record['log_join'] or False
        self.leave = record['leave'] or False
        self.kick = record['kick'] or False
        self.ban = record['ban'] or False
        self.welcome = record['welcome_enabled'] or False
        self.welcome_channel = record['welcome_channel'] or None
        self.commands = record['log_commands'] or False
        self.unban = record['unban'] or False
        self.buy_roles = record['buy_roles'] or False
        self.advert = record['advert'] or False
        self.logging_channel = record['logging_channel'] or None
        self.enabled = record['enabled'] or False
        self.advert_bypass = record['advert_bypass'] or None

    async def edit_field(self, **fields):
        keys = ', '.join(fields)
        values = ', '.join(f'${2 + i}' for i in range(len(fields)))

        query = f"""UPDATE settings
                    SET {keys} = {values}
                    WHERE id=$1;
                 """
        _values = [_ for _ in fields.values()]

        for index, key in enumerate(fields):
            self.__dict__[key] = _values[index]

        await self.bot.pool.execute(query, self.id, *fields.values())

class Settings():
    def __init__(self, bot):
        self.bot = bot

    async def get_settings(self, id):
        record = await self.bot.pool.fetchrow('SELECT * FROM settings WHERE id=$1;', id)
        if not record:
            await self.bot.pool.execute('INSERT INTO settings (id) values ($1);', id)
            record = await self.bot.pool.fetchrow('SELECT * FROM settings WHERE id=$1;', id)
        return SettingsConfig(self.bot, record)
    
    @commands.command()
    @checks.has_permissions(administrator=True)
    async def settings(self, ctx):
        if not ctx.invoked_subcommand:
            
            embed = discord.Embed(color=discord.Color.dark_teal(), title='Settings', description='Configure this server\'s settings.')
            embed.add_field(
                name="Logging",
                value="Toggles a logging module.\n"\
                      "``logging <module>``\n"\
                      "Valid modules are: ``kick``, ``ban``, ``leave``, ``commands``, ``message_edit``, ``message_delete``",
                       inline=True)
            embed.add_field(
                name="Prefix",
                value="Configrues the prefix for this server.\n"\
                      "``prefix <add|remove> <prefix>``\n"\
                      "Put the prefix in \"quotes\" to make it have spaces.",
                      inline=True)
            embed.add_field(
                name="Starboard",
                value="Sets up a starboard.\n"\
                      "``starboard [name of the starboard channel]``")
            embed.add_field(
                name="Buy roles",
                value="Toggles role buying.\n"\
                      "``buy_roles``")
            embed.add_field(
                name="Anti advertising",
                value="Toggles anti advertising\n"\
                      "``antiadvert``")
            embed.add_field(
                name="Anti raid",
                value=""
            )
            embed.set_footer(text="For more information search across the help menu.")

            await ctx.send(embed=embed)

    @commands.command()
    @checks.is_admin()
    async def buy_roles(self, ctx):
        settings = await self.get_settings(ctx.guild.id)
        settings.buy_roles = not settings.buy_roles
        await settings.edit_field(buy_roles=settings.buy_roles)
        state = 'enabled' if settings.buy_roles else 'disabled'
        await ctx.send(f'{ctx.tick(True)} Role buying is now {state}.')

    @commands.command()
    @checks.is_admin()
    async def antiadvert(self, ctx):
        settings = await self.get_settings(ctx.guild.id)
        settings.advert = not settings.advert
        await settings.edit_field(advert=settings.advert)
        state = 'enabled' if settings.advert else 'disabled'
        await ctx.send(f'{ctx.tick(True)} Anti advertising is now {state}.')

    @commands.group()
    @checks.is_mod()
    async def logging(self, ctx):
        if not ctx.invoked_subcommand:
            return await ctx.show_help('logging')

    @logging.command()
    async def message_edit(self, ctx):
        settings = await self.get_settings(ctx.guild.id)
        settings.message_edit = not settings.message_edit
        await settings.edit_field(message_edit=settings.message_edit)
        state = 'enabled' if settings.message_edit else 'disabled'
        await ctx.send(f'{ctx.tick(True)} Message edit logging is now {state}.')

    @logging.command()
    async def message_delete(self, ctx):
        settings = await self.get_settings(ctx.guild.id)
        settings.message_delete = not settings.message_delete
        await settings.edit_field(message_delete=settings.message_delete)
        state = 'enabled' if settings.message_delete else 'disabled'
        await ctx.send(f'{ctx.tick(True)} Message delete logging is now {state}.')

    @logging.command()
    async def join(self, ctx):
        settings = await self.get_settings(ctx.guild.id)
        settings.join = not settings.join
        await settings.edit_field(log_join=settings.join)
        state = 'enabled' if settings.buy_roles else 'disabled'
        await ctx.send(f'{ctx.tick(True)} Join logging is now {state}.')

    @logging.command()
    async def leave(self, ctx):
        settings = await self.get_settings(ctx.guild.id)
        settings.leave = not settings.leave
        await settings.edit_field(leave=settings.leave)
        state = 'enabled' if settings.leave else 'disabled'
        await ctx.send(f'{ctx.tick(True)} Leave logging is now {state}.')

    @logging.command()
    async def kick(self, ctx):
        settings = await self.get_settings(ctx.guild.id)
        settings.kick = not settings.kick
        await settings.edit_field(kick=settings.kick)
        state = 'enabled' if settings.kick else 'disabled'
        await ctx.send(f'{ctx.tick(True)} Kick logging is now {state}.')

    @logging.command()
    async def ban(self, ctx):
        settings = await self.get_settings(ctx.guild.id)
        settings.ban = not settings.ban
        await settings.edit_field(ban=settings.ban)
        state = 'enabled' if settings.ban else 'disabled'
        await ctx.send(f'{ctx.tick(True)} Ban logging is now {state}.')

    @logging.command()
    async def unban(self, ctx):
        settings = await self.get_settings(ctx.guild.id)
        settings.unban = not settings.unban
        await settings.edit_field(unban=settings.unban)
        state = 'enabled' if settings.unban else 'disabled'
        await ctx.send(f'{ctx.tick(True)} Unban logging is now {state}.')

    @logging.command()
    async def commands(self, ctx):
        settings = await self.get_settings(ctx.guild.id)
        settings.commands = not settings.commands
        await settings.edit_field(log_commands=settings.commands)
        state = 'enabled' if settings.buy_roles else 'disabled'
        await ctx.send(f'{ctx.tick(True)} Command logging is now {state}.')

    async def on_message(self, message):
        if not message.guild: return
        ctx = await self.bot.get_context(message)
        settings = await self.get_settings(ctx.guild.id)
        if not settings: return
        if not settings.advert: return
        resolved = ctx.author.guild_permissions
        if getattr(resolved, 'manage_messages', None) == True: return
        for role in ctx.author.roles:
            if role.id in settings.advert_bypass:
                return
        if 'https://discord.gg/' in message.content:
            try:
                await message.delete()
                await message.channel.send('Don\'t advertise here dude.', delete_after=10)
            except discord.Forbidden:
                pass
        elif 'discord.gg/' in message.content:
            try:
                await message.delete()
                await message.channel.send('Don\'t advertise here dude.', delete_after=10)
            except discord.Forbidden:
                pass

def setup(bot):
    bot.add_cog(Settings(bot))
