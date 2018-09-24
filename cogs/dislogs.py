from discord.ext import commands
import discord
import discord.utils
from .utils import config
import json
from discord.utils import find, get
import datetime
import asyncio
import aiohttp
from .utils import checks, context

class Settings:
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

class DisLogs:
    def __init__(self, bot):
        self.bot = bot

    async def post(self, content):
        async with aiohttp.ClientSession() as session:
            async with session.post("https://hastebin.com/documents",data=content.encode('utf-8')) as post:
                post = await post.json()
                return f"https://hastebin.com/{post['key']}"

    async def get_settings(self, id):
        record = await self.bot.pool.fetchrow(f'select * from settings where id={id}')
        return Settings(self.bot, record)

    async def on_message_delete(self, message):
        if message.author.bot: return
        settings = await self.get_settings(message.guild.id)
        if not settings: return
        if not settings.message_delete: return
        if not settings.logging_channel: return
        e = discord.Embed(description=f'{message.content}\n\nHas been deleted in {message.channel.mention}.', color=discord.Color.red())
        e.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        try:
            async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
                e.set_footer(text=f'Deleted by {entry.user.display_name} at')
        except discord.Forbidden:
            e.set_footer(text='If you want to see who delete this, I need audit log permissions. This message was delete at')

        e.timestamp = datetime.datetime.utcnow()
        ch = message.guild.get_channel(settings.logging_channel)
        if ch:
            await ch.send(embed=e)

    async def on_message_edit(self, before, after):
        if before.author.bot: return
        settings = await self.get_settings(before.guild.id)
        if not settings: return
        if not settings.message_edit: return
        if not settings.logging_channel: return
        e = discord.Embed(color=discord.Color.teal())
        e.set_author(name=before.author.display_name, icon_url=after.author.avatar_url)
        e.add_field(name="Before", value=before.content, inline=False)
        e.add_field(name="After", value=after.content, inline=False)
        e.add_field(name=f"({after.id}) has been edited", value=f"in {before.channel.mention}.", inline=False)
        e.timestamp = datetime.datetime.utcnow()
        ch = before.guild.get_channel(settings.logging_channel)
        if ch:
            await ch.send(embed=e)
        
    async def on_member_leave(self, member):
        settings = await self.get_settings(member.guild.id)
        if not settings: return
        if not settings.leave: return
        if not settings.logging_channel: return
        target = 'member' if not member.bot else 'bot'
        e = discord.Embed(title=f'A {target} has joined the guild.', color=member.top_role.color)
        e.add_field(name='Name:', value=member.display_name, inline=False)
        e.add_field(name="Members now:", value=len(member.guild.members), inline=False)
        e.timestamp = datetime.datetime.utcnow()
        ch = member.guild.get_channel(settings.logging_channel)
        if ch:
            await ch.send(embed=e)

    async def on_member_remove(self, member):
        settings = await self.get_settings(member.guild.id)
        if not settings: return
        if not settings.kick: return
        if not settings.logging_channel: return
        try:
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if entry.target.id == member.id:
                    return
        except discord.Forbidden:
            pass
        target = 'bot' if member.bot else 'member'
        e = discord.Embed(title=f'A {target} has left the guild.', color=member.top_role.color)
        e.add_field(name='Name:', value='{}'.format(member.name), inline=False)
        e.add_field(name="Members now:", value='{}'.format(len(member.guild.members)), inline=False)
        try:
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                if not entry.target.id == member.id: return
                e.add_field(name="Action by:", value=entry.user.display_name, inline=False)
                e.add_field(name="Reason:", value=entry.reason, inline=False)
        except discord.Forbidden:
            e.set_footer(text="If you want to see who did this enable audits logs.")
        e.timestamp = datetime.datetime.utcnow()
        ch = member.guild.get_channel(settings.logging_channel)
        if ch:
            await ch.send(embed=e)

    async def on_member_ban(self, guild, member):
        settings = await self.get_settings(member.guild.id)
        if not settings: return
        if not settings.ban: return
        if not settings.logging_channel: return
        target = 'bot' if member.bot else 'member'
        e = discord.Embed(title=f'A {target} has been banned from the guild.', color=member.top_role.color)
        e.add_field(name='Name:', value='{}'.format(member.name), inline=False)
        e.add_field(name="Members now:", value=len(member.guild.members), inline=False)
        try:
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if not entry.target.id == member.id: return
                e.add_field(name="Action by:", value=entry.user, inline=False)
                e.add_field(name="Reason:", value=entry.reason, inline=False)
        except discord.Forbidden:
            e.set_footer(text="If you want to see who did this enable audits logs.")
        e.timestamp = datetime.datetime.utcnow()
        ch = guild.get_channel(settings.logging_channel)
        if ch:
            await ch.send(embed=e)

    async def on_member_unban(self, guild, user):
        settings = await self.get_settings(guild.id)
        if not settings: return
        if not settings.unban: return
        if not settings.logging_channel: return
        target = 'bot' if user.bot else 'user'
        e = discord.Embed(title=f'A {target} has been unbanned from the guild.')
        e.add_field(name='Name:', value=user.name, inline=False)
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
                if not entry.target.id == user.id: return
                e.add_field(name="Action by:", value=entry.user, inline=False)
                e.add_field(name="Reason:", value=entry.reason, inline=False)
        except discord.Forbidden:
            e.set_footer(text="If you want to see who did this enable audits logs.")
        e.timestamp = datetime.datetime.utcnow()
        ch = guild.get_channel(settings.logging_channel)
        if ch:
            await ch.send(embed=e)

    async def on_command(self, ctx):
        settings = await self.get_settings(ctx.guild.id)
        if not settings: return
        if not settings.commands: return
        if not settings.logging_channel: return
        ch = ctx.guild.get_channel(settings.logging_channel)
        await ch.send(f'``{ctx.author}`` ran ``{ctx.prefix}{ctx.command}`` in {ctx.channel.mention}.')
        
    @commands.group()
    @checks.is_mod()
    async def welcome(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.show_help('welcome')

    @welcome.command(name='toggle')
    @checks.is_mod()
    async def welcome_toggle(self, ctx):
        """Toggles welcome messages."""
        settings = await self.get_settings(ctx.guild.id)
        settings.welcome = not settings.welcome
        state = 'enabled' if settings.welcome else 'disabled'
        await ctx.send(f'Welcome message is now {state}.')
        if not settings.welcome:
            await ctx.send(f'{ctx.tick(False)} Don\'t forget to set the channel with `{ctx.prefix}wecome channel`.')

    @welcome.command(name='channel')
    @checks.is_mod()
    async def welcome_channel(self, ctx, channel:discord.TextChannel=None):
        settings = await self.get_settings(ctx.guild.id)
        if not settings.welcome:
            return await ctx.send(f'{ctx.tick(False)} Welcome messages are not enabled. Run `.welcome toggle` to enable them.')
        if not channel:
            return await ctx.send(f'{ctx.tick(False)} You forgot to mention the channel to send welcome messages.')
        await settings.edit_field(welcome_channel=channel.id)
        await ctx.send(f'{ctx.tick(True)} Welcome channel edited. Now sending welcome messages to {channel}.')

    async def on_member_join(self, member):
        settings = await self.get_settings(member.guild.id)
        if not settings: return
        if not settings.welcome: return
        if not settings.welcome_channel: return
        e = discord.Embed(title=f"Welcome {member.display_name}!", color=member.top_role.color)
        e.set_image(url=f'https://kaan.ga/api/welcome/{member.display_name}/{member.id}/{member.avatar}')
        ch = member.guild.get_channel(settings.welcome_channel)
        await ch.send(embed=e)

def setup(bot):
    bot.add_cog(DisLogs(bot))
