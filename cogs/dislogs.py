from discord.ext import commands
import discord
import discord.utils
from .utils import config
import json

class LoggingInfo:
    def __init__(self, guild_id, channel):
        self.guild_id = guild_id
        self.channel = channel

    def __str__(self):
        output = []
        output.append('Channel: {0.channel}'.format(self))

class LoggingEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, LoggingInfo):
            payload = obj.__dict__.copy()
            payload['__logging__'] = False
            return payload
        return json.JSONEncoder.default(self, obj)

def logging_decoder(obj):
    if '__logging__' in obj:
        return LoggingInfo(**obj)
    return obj

class DisLogs:
    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('logs.json', encoder=LoggingEncoder, object_hook=logging_decoder, loop=bot.loop, load_later=False)

    @commands.command(invoke_without_command=False)
    @commands.has_permissions(manage_guild=True)
    async def enablelogging(self, ctx, *, channel: discord.TextChannel=None):
        """Enables logging for this guild to the text channel you specify."""
        if channel is None:
            await ctx.send('You forgot to tag a channel.')
            return

        await self.config.put(ctx.message.guild.id, channel.id)
        await ctx.send('Logging channel has been set to {}.'.format(channel))

    @commands.command(invoke_without_command=False)
    @commands.has_permissions(manage_guild=True)
    async def disablelogging(self, ctx):
        """Disables logging for this server."""
        await self.config.remove(str(ctx.message.guild.id))
        await ctx.send('Logging has been disabled on this guild.')

    async def on_message_delete(self, message):
        with open('logs.json') as file:
            data = json.load(file)
        try:
            async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
                if entry.user.id is 462020151869571092 or 460846291300122635:
                    return
        except discord.Forbidden:
            pass
        if str(message.guild.id) in data:
            data_channel = data[str(message.guild.id)]
            send_channel = self.bot.get_channel(int(data_channel))
            e = discord.Embed(title='A message has been deleted.', description='A message has been deleted at ``{}``.'.format(message.channel), color=discord.Color.red())
            # e.add_field(name='Content:', value='{}'.format(message.clean_content), inline=False)
            # e.add_field(name="Sent by:", value='{}'.format(message.author), inline=False)
            # e.add_field(name="Sent at:", value='{}'.format(message.created_at), inline=False)
            # if message.edited_at is not None:
            #     e.add_field(name="Edited at:", value='{}'.format(message.edited_at), inline=False)
            # try:
            #     async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
            #         if entry.user.id == message.user.id:
            #             e.add_field(title="Action by:", value="{}".format(entry.user), inline=False)
            # except discord.Forbidden:
            #     e.set_footer(text="If you want to see who did this enable audits logs.")
            # await channel.send('``{}`` deleted a message, it was sent to ``{}`` and it\'s content was:\n```{}```'.format(message.author.name, message.channel, message.content))
            await send_channel.send(embed=e)
        else:
            return

    async def on_message_edit(self, before, after):
        if before.author.bot: return
        with open('logs.json') as file:
            data = json.load(file)
            if str(before.guild.id) in data:
                data_channel = data[str(before.guild.id)]
                send_channel = self.bot.get_channel(int(data_channel))
                e = discord.Embed(title='A message has been edited.', description='A message has been edited at ``{}``.'.format(before.channel), color=discord.Color.gold())
                e.add_field(name='Before:', value='{}'.format(before.clean_content), inline=False)
                e.add_field(name='After:', value='{}'.format(after.clean_content), inline=False)
                e.add_field(name="Sent by:", value='{}'.format(before.author), inline=False)
                e.add_field(name="Sent at:", value='{}'.format(before.created_at), inline=False)
                e.add_field(name="Edited at:", value='{}'.format(after.edited_at), inline=False)

                # await channel.send('``{}`` edited a message, it was sent to ``{}`` and it\'s content before editing was:\n```{}```And after editing it is:\n```{}```'.format(before.author.name, before.channel, before.content, after.content))
                await send_channel.send(embed=e)

    async def on_guild_channel_create(self, channel):
        with open('logs.json') as file:
            data = json.load(file)
            if str(channel.guild.id) in data:
                data_channel = data[str(channel.guild.id)]
                send_channel = self.bot.get_channel(int(data_channel))
                e = discord.Embed(title='A channel has been created.', description=' ', color=discord.Color.green())
                e.add_field(name='Name:', value='{}'.format(channel.name), inline=False)
                if isinstance(channel, discord.TextChannel):
                    e.add_field(name="Type :", value='Tect Channel', inline=False)
                if isinstance(channel, discord.VoiceChannel):
                    e.add_field(name="Type:", value='Voice Channel', inline=False)
                e.add_field(name="Created at:", value='{}'.format(channel.created_at), inline=False)
                if isinstance(channel, discord.VoiceChannel):
                    e.add_field(name="User limit:", value='{}'.format(channel.user_limit), inline=False)
                if isinstance(channel, discord.TextChannel):
                    if channel.topic:
                        e.add_field(name="Topic:", value='{}'.format(channel.topic), inline=False)
                try:
                    async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
                        e.add_field(name="Action by:", value=entry.user, inline=False)
                        e.add_field(name="Reason:", value=entry.reason, inline=False)
                except discord.Forbidden:
                    e.set_footer(text="If you want to see who did this enable audits logs.")
                await send_channel.send(embed=e)
            else:
                return

    async def on_guild_channel_delete(self, channel):
        with open('logs.json') as file:
            data = json.load(file)
            if str(channel.guild.id) in data:
                data_channel = data[str(channel.guild.id)]
                send_channel = self.bot.get_channel(int(data_channel))
                e = discord.Embed(title='A channel has been deleted.', description=' ', color=discord.Color.red())
                e.add_field(name='Name:', value='{}'.format(channel.name), inline=False)
                if isinstance(channel, discord.TextChannel):
                    e.add_field(name="Type :", value='Tect Channel', inline=False)
                if isinstance(channel, discord.VoiceChannel):
                    e.add_field(name="Type:", value='Voice Channel', inline=False)
                if isinstance(channel, discord.TextChannel):
                    if channel.topic:
                         e.add_field(name="Topic:", value='{}'.format(channel.topic), inline=False)
                if isinstance(channel, discord.VoiceChannel):
                    e.add_field(name="User limit:", value='{}'.format(channel.user_limit), inline=False)
                e.add_field(name="Created at:", value='{}'.format(channel.created_at), inline=False)
                try:
                    async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
                        e.add_field(name="Action by:", value=entry.user, inline=False)
                        e.add_field(name="Reason:", value=entry.reason, inline=False)
                except discord.Forbidden:
                    e.set_footer(text="If you want to see who did this enable audits logs.")
                await send_channel.send(embed=e)
            else:
                return

    async def on_guild_channel_update(self, before, after):
        with open('logs.json') as file:
            data = json.load(file)
            if str(before.guild.id) in data:
                data_channel = data[str(before.guild.id)]
                send_channel = self.bot.get_channel(int(data_channel))
                e = discord.Embed(title='A channel has been edited.', description='Info:', color=discord.Color.gold())
                e.add_field(name='Name before:', value='{}'.format(before.name), inline=False)
                e.add_field(name='Name after:', value='{}'.format(after.name), inline=False)
                if isinstance(before, discord.TextChannel):
                    e.add_field(name="Type :", value='Tect Channel', inline=False)
                    if before.topic:
                        e.add_field(name="Topic before:", value='{}'.format(before.topic), inline=False)
                    if after.topic:
                        e.add_field(name="Topic after:", value='{}'.format(after.topic), inline=False)
                if isinstance(before, discord.VoiceChannel):
                    e.add_field(name="Type:", value='Voice Channel', inline=False)
                    e.add_field(name="User limit before:", value='{}'.format(before.user_limit), inline=False)
                    e.add_field(name="User limit after:", value='{}'.format(after.user_limit), inline=False)
                e.add_field(name="Created at:", value='{}'.format(before.created_at, inline=False))
                try:
                    async for entry in before.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update):
                        e.add_field(name="Action by:", value=entry.user, inline=False)
                        e.add_field(name="Reason:", value=entry.reason, inline=False)
                except discord.Forbidden:
                    e.set_footer(text="If you want to see who did this enable audits logs.")
                await send_channel.send(embed=e)
            else:
                return

    async def on_member_join(self, member):
        with open('logs.json') as file:
            data = json.load(file)
            if str(member.guild.id) in data:
                data_channel = data[str(member.guild.id)]
                send_channel = self.bot.get_channel(int(data_channel))
                target = 'member' if not member.bot else 'bot'
                e = discord.Embed(title='A {} has joined the guild.'.format(target), description=' ', color=discord.Color.green())
                e.add_field(name='Name:', value='{}'.format(member.name), inline=False)
                e.add_field(name="Joined at:", value='{}'.format(member.joined_at), inline=False)
                e.add_field(name="Members now:", value='{}'.format(len(member.guild.members)), inline=False)
                try:
                    async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.invite_update):
                        e.add_field(title="Inviter:", value=entry.inviter, inline=False)
                        e.add_field(title="Invite uses:", value=entry.uses, inline=False)
                except discord.Forbidden:
                    e.set_footer(text="If you want to see who ivnited him/her enable audits logs.")
                await send_channel.send(embed=e)

    async def on_member_remove(self, member):
        with open('logs.json') as file:
            try:
                async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                    if entry.target.id == member.id:
                        return
            except discord.Forbidden:
                pass
            data = json.load(file)
            if str(member.guild.id) in data:
                data_channel = data[str(member.guild.id)]
                send_channel = self.bot.get_channel(int(data_channel))
                e = discord.Embed(title='A member has left the guild.', description='We\'ll hope to see you soon!', color=discord.Color.red())
                e.add_field(name='Name:', value='{}'.format(member.name), inline=False)
                e.add_field(name="Members now:", value='{}'.format(len(member.guild.members)), inline=False)
                try:
                    async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                        if not entry.target.id == member.id: return
                        e.add_field(name="Action by:", value=entry.user, inline=False)
                        e.add_field(name="Reason:", value=entry.reason, inline=False)
                except discord.Forbidden:
                    e.set_footer(text="If you want to see who did this enable audits logs.")
                await send_channel.send(embed=e)

    async def on_member_ban(self, guild, member):
        with open('logs.json') as file:
            data = json.load(file)
            if str(guild.id) in data:
                data_channel = data[str(member.guild.id)]
                send_channel = self.bot.get_channel(int(data_channel))
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
                await send_channel.send(embed=e)

    async def on_member_unban(self, guild, user):
        with open('logs.json') as file:
            data = json.load(file)
            if str(guild.id) in data:
                data_channel = data[str(guild.id)]
                send_channel = self.bot.get_channel(int(data_channel))
                e = discord.Embed(title='A user has been unbanned from the guild.', color=discord.Color.red())
                e.add_field(name='Name:', value='{}'.format(user.name), inline=False)
                try:
                    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
                        if not entry.target.id == user.id: return
                        e.add_field(name="Action by:", value=entry.user, inline=False)
                        e.add_field(name="Reason:", value=entry.reason, inline=False)
                except discord.Forbidden:
                    e.set_footer(text="If you want to see who did this enable audits logs.")
                await send_channel.send(embed=e)

def setup(bot):
    bot.add_cog(DisLogs(bot))
