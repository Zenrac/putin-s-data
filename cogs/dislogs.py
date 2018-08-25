from discord.ext import commands
import discord
import discord.utils
from .utils import config
import json
from discord.utils import find, get
import datetime
# from .utils import db

class DisLogs:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(invoke_without_command=False)
    @commands.has_permissions(manage_guild=True)
    async def enablelogging(self, ctx, *, channel: discord.TextChannel=None):
        """Enables logging for this guild to the text channel you specify."""
        if channel is None:
            await ctx.send('You forgot to tag a channel.')
            return
        await ctx.bot.pool.execute('update settings set logging_enable=true where id={}'.format(ctx.guild.id))
        await ctx.send('Logging channel has been set to {}.'.format(channel))

    @commands.command(invoke_without_command=False)
    @commands.has_permissions(manage_guild=True)
    async def disablelogging(self, ctx):
        """Disables logging for this server."""
        await ctx.bot.pool.execute('update settings set logging_enable=false where id={}'.format(ctx.guild.id))
        await ctx.send('Logging has been disabled on this guild.')

    async def on_message_delete(self, message):
        if message.author.bot: return
        try:
            send_channel = get(message.guild.text_channels, name='putin-logging')
        except:
            return
        if send_channel is None: return
        try:
            async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
                if entry.user.bot:
                    return
        except discord.Forbidden:
            pass
        except Exception as e:
            print(e)
        e = discord.Embed(description=f'{message.content}\n\nHas been deleted in {message.channel.mention}.', color=discord.Color.red())
        e.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        try:
            async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
                if entry.user.id == message.author.id:
                    e.add_field(name="Action by:", value="{}".format(entry.user), inline=False)
        except discord.Forbidden:
            e.set_footer(text="If you want to see who did this enable audits logs.")
        e.timestamp = datetime.datetime.utcnow()

        await send_channel.send(embed=e)

    async def on_message_edit(self, before, after):
        if before.author.bot: return
        try:
            send_channel = get(before.guild.text_channels, name='putin-logging')
        except:
            return
        if send_channel is None: return
        e = discord.Embed(color=discord.Color.teal())
        e.set_author(name=before.author.display_name, icon_url=after.author.avatar_url)
        e.add_field(name="Before", value=before.content, inline=False)
        e.add_field(name="After", value=after.content, inline=False)
        e.add_field(name=f"({after.id}) has been edited", value=f"in {before.channel.mention}.", inline=False)
        e.timestamp = datetime.datetime.utcnow()
        await send_channel.send(embed=e)

    async def on_member_join(self, member):
        try:
            send_channel = get(member.guild.text_channels, name='putin-logging')
        except:
            return
        if send_channel is None: return
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
        
    async def on_member_leave(self, member):
        try:
            send_channel = get(member.guild.text_channels, name='putin-logging')
        except:
            return
        if send_channel is None: return
        target = 'member' if not member.bot else 'bot'
        e = discord.Embed(title='A {} has joined the guild.'.format(target), description=' ', color=discord.Color.green())
        e.add_field(name='Name:', value='{}'.format(member.name), inline=False)
        e.add_field(name="Members now:", value='{}'.format(len(member.guild.members)), inline=False)
        e.timestamp = datetime.datetime.utcnow()
        await send_channel.send(embed=e)

    async def on_member_remove(self, member):
        try:
            send_channel = get(member.guild.text_channels, name='putin-logging')
        except:
            return
        if send_channel is None: return
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
            send_channel = get(member.guild.text_channels, name='putin-logging')
        except:
            return
        if send_channel is None: return
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
            send_channel = get(user.guild.text_channels, name='putin-logging')
        except:
            return
        if send_channel is None: return
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
            channel = get(ctx.guild.channels, name='putin-logging')
        except:
            pass
        if channel is None: return
        await channel.send(f'``{ctx.author}`` ran ``{ctx.prefix}{ctx.command}`` in {ctx.channel.mention}.')

def setup(bot):
    bot.add_cog(DisLogs(bot))
