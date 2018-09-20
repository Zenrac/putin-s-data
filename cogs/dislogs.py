from discord.ext import commands
import discord
import discord.utils
from .utils import config
import json
from discord.utils import find, get
import datetime
import asyncio
import aiohttp

class Settings:
    def __init__(self, bot, record):
        self.bot = bot
        self.message_delete = record['message_delete'] or False
        self.message_edit = record['message_edit'] or False
        self.join = record['log_join'] or False
        self.leave = record['leave'] or False
        self.kick = record['kick'] or False
        self.ban = record['ban'] or False
        self.welcome = record['welcome_enabled'] or False
        self.welcome_channel = record['welcome_channel']
        self.commands = record['log_commands']
        self.unban = record['unban']
        self.buy_roles = record['buy_roles']
        self.advert = record['advert']
        
    async def edit_field(**fields)
        pass

class DisLogs:
    def __init__(self, bot):
        self.bot = bot

    async def post(self, content):
        async with aiohttp.ClientSession() as session:
            async with session.post("https://hastebin.com/documents",data=content.encode('utf-8')) as post:
                post = await post.json()
                return "https://hastebin.com/{}".format(post['key'])

    async def get_settings(self, id):
        record = self.bot.pool.fetchrow(f'select * from settings where id={id}')
        return Settings(self.bot, record)

    async def on_message_delete(self, message):
        if message.author.bot: return
        try:
            send_channel = get(message.guild.text_channels, name='w-bot-logging')
        except:
            return
        if send_channel is None: return
        data = await self.bot.pool.fetchrow(f'select message_delete from settings where id={message.guild.id}')
        if not data: return
        if not data[0]: return
        try:
            deleted = []
            async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
                count = entry.extra.count
                if entry.extra.count >= 2:
                    deleted.append((entry.user.display_name, entry.extra.channel.name, message.content, 
                                    message.edited_at if message.edited_at else message.created_at))
            if count >= 2:
                url = await self.post("\n\n\n".join(f'{_[0]} in {_[1]} at {_[3]}\n  {_[2]}' for _ in deleted))
                e = discord.Embed(description=f"Bulk message delete in {message.channel.mention}", color=discord.Color.red())
                e.add_field(name='Messages', value=f'[Click here to see the messages.]({url})')
                e.timestamp = datetime.datetime.utcnow()
                return await send_channel.send(embed=e)
            else:
                pass
        except discord.Forbidden:
            pass
        except Exception as e:
            print(e)
        e = discord.Embed(description=f'{message.content}\n\nHas been deleted in {message.channel.mention}.', color=discord.Color.red())
        e.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()

        await send_channel.send(embed=e)

    async def on_message_edit(self, before, after):
        if before.author.bot: return
        try:
            send_channel = get(before.guild.text_channels, name='w-bot-logging')
        except:
            return
        if send_channel is None: return
        data = await self.bot.pool.fetchrow(f'select message_edit from settings where id={after.guild.id}')
        if not data: return
        if not data[0]: return
        e = discord.Embed(color=discord.Color.teal())
        e.set_author(name=before.author.display_name, icon_url=after.author.avatar_url)
        e.add_field(name="Before", value=before.content, inline=False)
        e.add_field(name="After", value=after.content, inline=False)
        e.add_field(name=f"({after.id}) has been edited", value=f"in {before.channel.mention}.", inline=False)
        e.timestamp = datetime.datetime.utcnow()
        await send_channel.send(embed=e)

    async def on_member_join(self, member):
        try:
            send_channel = get(member.guild.text_channels, name='w-bot-logging')
        except:
            return
        if send_channel is None: return
        data = await self.bot.pool.fetchrow(f'select log_join from settings where id={member.guild.id}')
        if not data: return
        if not data[0]: return
        target = 'member' if not member.bot else 'bot'
        e = discord.Embed(title='A {} has joined the guild.'.format(target), description=' ', color=discord.Color.green())
        e.add_field(name='Name:', value='{}'.format(member.name), inline=False)
        e.add_field(name="Members now:", value='{}'.format(len(member.guild.members)), inline=False)
        try:
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.invite_update):
                e.add_field(name="Inviter:", value=entry.inviter, inline=False)
                e.add_field(name="Invite uses:", value=entry.uses, inline=False)
        except discord.Forbidden:
            e.set_footer(text="If you want to see who invited him/her enable audits logs.")
        e.timestamp = datetime.datetime.utcnow()
        await send_channel.send(embed=e)

        settings = await self.get_settings(member.guild.id)
        if settings.welcome:
            ch = get(member.guild.text_channels, id=welcome_channel)
            e = discord.Embed(title="Welcome", color=member.top_role.color)
            e.set_image(url=f'https://kaan.ga/api/welcome/{member.display_name}/{member.id}/{member.avatar}')
        
    async def on_member_leave(self, member):
        try:
            send_channel = get(member.guild.text_channels, name='w-bot-logging')
        except:
            return
        if send_channel is None: return
        data = await self.bot.pool.fetchrow(f'select leave from settings where id={member.guild.id}')
        if not data: return
        if not data[0]: return
        target = 'member' if not member.bot else 'bot'
        e = discord.Embed(title='A {} has joined the guild.'.format(target), description=' ', color=discord.Color.green())
        e.add_field(name='Name:', value='{}'.format(member.name), inline=False)
        e.add_field(name="Members now:", value='{}'.format(len(member.guild.members)), inline=False)
        e.timestamp = datetime.datetime.utcnow()
        await send_channel.send(embed=e)

    async def on_member_remove(self, member):
        try:
            send_channel = get(member.guild.text_channels, name='w-bot-logging')
        except:
            return
        if send_channel is None: return
        data = await self.bot.pool.fetchrow(f'select kick from settings where id={member.guild.id}')
        if not data: return
        if not data[0]: return
        try:
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if entry.target.id == member.id:
                    return
        except discord.Forbidden:
            pass
        e = discord.Embed(title='A member has left the guild.', description=' ', color=discord.Color.red())
        e.add_field(name='Name:', value='{}'.format(member.name), inline=False)
        e.add_field(name="Members now:", value='{}'.format(len(member.guild.members)), inline=False)
        try:
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                if not entry.target.id == member.id: return
                e.add_field(name="Action by:", value=entry.user, inline=False)
                e.add_field(name="Reason:", value=entry.reason, inline=False)
        except discord.Forbidden:
            e.set_footer(text="If you want to see who did this enable audits logs.")
        e.timestamp = datetime.datetime.utcnow()
            
        await send_channel.send(embed=e)

    async def on_member_ban(self, guild, member):
        try:
            send_channel = get(member.guild.text_channels, name='w-bot-logging')
        except:
            return
        if send_channel is None: return
        if not data[0]: return
        data = await self.bot.pool.fetchrow(f'select ban from settings where id={guild.id}')
        if not data: return
        e = discord.Embed(title='A member has been banned from the guild.', color=discord.Color.red())
        e.add_field(name='Name:', value='{}'.format(member.name), inline=False)
        e.add_field(name="Members now:", value='{}'.format(len(member.guild.members)), inline=False)
        try:
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if not entry.target.id == member.id: return
                e.add_field(name="Action by:", value=entry.user, inline=False)
                e.add_field(name="Reason:", value=entry.reason, inline=False)
        except discord.Forbidden:
            e.set_footer(text="If you want to see who did this enable audits logs.")
        e.timestamp = datetime.datetime.utcnow()
        
        await send_channel.send(embed=e)

    async def on_member_unban(self, guild, user):
        try:
            send_channel = get(user.guild.text_channels, name='w-bot-logging')
        except:
            return
        if send_channel is None: return
        if not data[0]: return
        data = await self.bot.pool.fetchrow(f'select unban from settings where id={guild.id}')
        if not data: return
        e = discord.Embed(title='A user has been unbanned from the guild.', color=discord.Color.red())
        e.add_field(name='Name:', value='{}'.format(user.name), inline=False)
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
                if not entry.target.id == user.id: return
                e.add_field(name="Action by:", value=entry.user, inline=False)
                e.add_field(name="Reason:", value=entry.reason, inline=False)
        except discord.Forbidden:
            e.set_footer(text="If you want to see who did this enable audits logs.")
        e.timestamp = datetime.datetime.utcnow()
            
        await send_channel.send(embed=e)

    async def on_command(self, ctx):
        try:
            channel = get(ctx.guild.channels, name='w-bot-logging')
        except:
            pass
        data = await self.bot.pool.fetchrow(f'select log_commands from settings where id={ctx.guild.id}')
        if not data: 
            return
        if not data[0]: return
        if channel is None: return
        await channel.send(f'``{ctx.author}`` ran ``{ctx.prefix}{ctx.command}`` in {ctx.channel.mention}.')
        
    @commands.commad(hidden=True)
    @checks.is_mod()
    async def welcome(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.show_help('welcome')

    @welcome.command(hidden=True, name='toggle')
    @checks.is_mod()
    async def welcome_toggle(self, ctx, *, channel:discord.TextChannel=None):
        """Toggles welcome messages."""
        if not channel:
            return await ctx.send(f'{ctx.tick(False)} You need to mention a channel to toggle.')
        settings = await self.get_settings(ctx.guild.id)
        settings.welcome = not settings.welcome
        state = 'enabled' if settings.welcome else 'disabled'
        await ctx.send(f'Welcome message is now enabled.')

def setup(bot):
    bot.add_cog(DisLogs(bot))
