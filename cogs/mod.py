from discord.ext import commands
from .utils import config
from collections import Counter
import re
import discord
import asyncio
import argparse
import json

class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)

class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
        else:
            can_execute = ctx.author.id == ctx.bot.owner_id or \
                          ctx.author == ctx.guild.owner or \
                          ctx.author.top_role > m.top_role

            if not can_execute:
                raise commands.BadArgument('You cannot do this action on this user due to role hierarchy.')
            return m.id

class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        ban_list = await ctx.guild.bans()
        try:
            member_id = int(argument, base=10)
            entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
        except ValueError:
            entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument("Not a valid previously-banned member.")
        return entity

class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = f'{ctx.author} (ID: {ctx.author.id}): {argument}'

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret


class Mod():
    """Moderation related commands."""
    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('mod.json', loop=bot.loop)

    def bot_user(self, message):
        return message.guild.me if message.channel.is_private else self.bot.user

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def createrole(self, ctx, role : str = None):
        """Creates a role to the guild."""
        if role is None:
            await ctx.send('You did not tell me what is the role\'s name.')
        else:
            await ctx.guild.create_role(name=role)
            await ctx.send('I created the role {}.'.format('@' + role))

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def addrole(self, ctx, member: discord.Member = None, role: discord.Role = None, reason: str = None):
        if member is None:
            return await ctx.send('You didn\'t give me the member.')
        if role is None:
            return await ctx.send('You didn\'t give me the role.')
        try:
            await member.add_roles(roles=role, reason=reason)
            await ctx.send('Role added.')
        except:
            pass

    # @commands.command(hidden=True)
    # @commands.has_permissions(manage_channel=True)
    # async def pin(self, ctx):
    #
    #     message = ctx.message.content
    #     message = message.replace(".pin ", '')
    #     msg = await self.bot.send_message(ctx.message, message)
    #     await self.bot.pin_message(msg)

    @commands.group(no_pm=True)
    @commands.has_permissions(manage_channel=True)
    async def ignore(self, ctx):
        """Handles the bot's ignore lists.
        To use these commands, you must have the Bot Admin role or have
        Manage Channel permissions. These commands are not allowed to be used
        in a private message context.
        Users with Manage Roles or Bot Admin role can still invoke the bot
        in ignored channels.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid subcommand passed: {0.subcommand_passed}'.format(ctx))

    @ignore.command(name='channel')
    async def channel_cmd(self, ctx, *, channel : discord.TextChannel = None):
        """Ignores a specific channel from being processed.
        If no channel is specified, the current channel is ignored.
        If a channel is ignored then the bot does not process commands in that
        channel until it is unignored.
        """

        if channel is None:
            channel = ctx.message.channel

        ignored = self.config.get('ignored', [])
        if str(channel.id) in ignored:
            await ctx.send(':exclamation: | That channel is already ignored.')
            return

        ignored.append(str(channel.id))
        await self.config.put('ignored', ignored)
        await ctx.send(':ballot_box_with_check:')

    @ignore.command(name='all', )
    @commands.has_permissions(manage_guild=True)
    async def _all(self, ctx):
        """Ignores every channel in the guild from being processed.
        This works by adding every channel that the guild currently has into
        the ignore list. If more channels are added then they will have to be
        ignored by using the ignore command.
        To use this command you must have Manage guild permissions along with
        Manage Channel permissions. You could also have the Bot Admin role.
        """

        ignored = self.config.get('ignored', [])
        channels = ctx.message.guild.channels
        ignored.extend(str(c.id) for c in channels if c.type == discord.ChannelType.text)
        await self.config.put('ignored', list(set(ignored))) # make unique
        await ctx.send(':ballot_box_with_check:')

    @commands.command(no_pm=True)
    @commands.has_permissions(manage_channel=True)
    async def unignore(self, ctx, *, channel : discord.TextChannel = None):
        """Unignores a specific channel from being processed.
        If no channel is specified, it unignores the current channel.
        To use this command you must have the Manage Channel permission or have the
        Bot Admin role.
        """

        if channel is None:
            channel = ctx.message.channel

        # a set is the proper data type for the ignore list
        # however, JSON only supports arrays and objects not sets.
        ignored = self.config.get('ignored', [])
        try:
            ignored.purge(str(channel.id))
        except ValueError:
            await ctx.send(':exclamation: | Channel was not ignored in the first place.')
        else:
            await ctx.send(':ballot_box_with_check:')

    @commands.command(no_pm = True)
    @commands.has_permissions(manage_channel=True)
    async def editchannelname(self, ctx, channel : discord.abc.GuildChannel = None, *, newchannelname : str = None):
        """Edits a channel's name."""
        if channel is None:
            await ctx.send('You did not tell me which channel to edit.')
        elif newchannelname is None:
            await ctx.send('You did not tell me what to change it to.')
        else:
            try:
                await ctx.message.delete()
            except:
                pass
            await channel.edit(name=newchannelname)
            await ctx.send(':ballot_box_with_check: | {} changed the name of #{}#{}.'.format(ctx.message.author.name, channel.name, channel.discriminator))

    @commands.command(no_pm = True)
    @commands.has_permissions(manage_guild=True)
    async def mute(self, ctx, *, user : discord.Member):
        """Mutes a user."""
        try:
            await user.edit(mute=True)
            await ctx.send(':ballot_box_with_check: | {} muted {}.'.format(ctx.message.author.name, user.name))
        except discord.Forbidden:
            await ctx.send(':exclamation: | The bot does not have proper permissions.')
        except discord.HTTPException:
            await ctx.send(':exclamation: | Muting failed.')

    @commands.command(no_pm = True)
    @commands.has_permissions(manage_guild=True)
    async def unmute(self, ctx, *, user : discord.Member):
        """Unmutes a user."""
        try:
            await user.edit(mute=False)
            await ctx.send(':ballot_box_with_check: | {} unmuted {}.'.format(ctx.message.author.mention, user.mention))
        except discord.Forbidden:
            await ctx.send(':exclamation: | The bot does not have proper permissions.')
        except discord.HTTPException:
            await ctx.send(':exclamation: | Unmuting failed.')

    @commands.command(no_pm = True)
    @commands.has_permissions(manage_guild=True)
    async def deafen(self, ctx, *, user : discord.Member):
        """Deafens a user."""
        try:
            await user.edit(deafen=True)
            await ctx.send(':ballot_box_with_check: | {} deafened {}.'.format(ctx.message.author.mention, user.mention))
        except discord.Forbidden:
            await ctx.send(':exclamation: | The bot does not have proper permissions.')
        except discord.HTTPException:
            await ctx.send(':exclamation: | Deafening failed.')

    @commands.command(no_pm = True)
    @commands.has_permissions(manage_guild=True)
    async def undeafen(self, ctx, *, user : discord.Member):
        """Undeafens a user."""
        try:
            await user.edit(deafen=False)
            await ctx.send(':ballot_box_with_check: | {} undeafened {}.'.format(ctx.message.author.mention, user.mention))
        except discord.Forbidden:
            await ctx.send(':exclamation: | The bot does not have proper permissions.')
        except discord.HTTPException:
            await ctx.send(':exclamation: | Undeafening failed.')

    async def _basic_cleanup_strategy(self, ctx, search):
        count = 0
        async for msg in ctx.history(limit=search, before=ctx.message):
            if msg.author == ctx.me:
                await msg.delete()
                count += 1
        return { 'Bot': count }

    async def _complex_cleanup_strategy(self, ctx, search):
        with open('prefixes.json') as f:
            data = json.read(f)

        if str(ctx.guild.id) in data:
            prefix = data[str(ctx.guild.id)]
        else:
            prefix = None
        def check(m):
            return m.author == ctx.me or m.content.startswith('.') or m.content.startswith('<@460846291300122635> ') or m.content.startswith(prefix)
        deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
        return Counter(m.author.display_name for m in deleted)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def cleanup(self, ctx, search=100):
        """Cleans up the bot's messages from the channel.
        If a search number is specified, it searches that many messages to delete.
        If the bot has Manage Messages permissions then it will try to delete
        messages that look like they invoked the bot as well.
        After the cleanup is completed, the bot will send you a message with
        which people got their messages deleted and their count. This is useful
        to see which users are spammers.
        You must have Manage Messages permission to use this.
        """

        strategy = self._basic_cleanup_strategy
        # if ctx.me.permissions_in(ctx.channel).manage_messages:
        #     strategy = self._complex_cleanup_strategy

        spammers = await strategy(ctx, search)
        deleted = sum(spammers.values())
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'- **{author}**: {count}' for author, count in spammers)

        await ctx.send('\n'.join(messages), delete_after=10)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: ActionReason = None):
        """Kicks a member from the server.
        In order for this to work, the bot must have Kick Member permissions.
        To use this command you must have Kick Members permission.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await member.kick(reason=reason)
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: MemberID, *, reason: ActionReason = None):
        """Bans a member from the server.
        You can also ban from ID to ban regardless whether they're
        in the server or not.
        In order for this to work, the bot must have Ban Member permissions.
        To use this command you must have Ban Members permission.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.ban(discord.Object(id=member), reason=reason)
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def massban(self, ctx, reason: ActionReason, *members: MemberID):
        """Mass bans multiple members from the server.
        You can also ban from ID to ban regardless whether they're
        in the server or not.
        Note that unlike the ban command, the reason comes first
        and is not optional.
        In order for this to work, the bot must have Ban Member permissions.
        To use this command you must have Ban Members permission.
        """

        for member_id in members:
            await ctx.guild.ban(discord.Object(id=member_id), reason=reason)

        await ctx.send('\N{OK HAND SIGN}')

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def softban(self, ctx, member: MemberID, *, reason: ActionReason = None):
        """Soft bans a member from the server.
        A softban is basically banning the member from the server but
        then unbanning the member as well. This allows you to essentially
        kick the member while removing their messages.
        In order for this to work, the bot must have Ban Member permissions.
        To use this command you must have Kick Members permissions.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        obj = discord.Object(id=member)
        await ctx.guild.ban(obj, reason=reason)
        await ctx.guild.unban(obj, reason=reason)
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: BannedMember, *, reason: ActionReason = None):
        """Unbans a member from the server.
        You can pass either the ID of the banned member or the Name#Discrim
        combination of the member. Typically the ID is easiest to use.
        In order for this to work, the bot must have Ban Member permissions.
        To use this command you must have Ban Members permissions.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.unban(member.user, reason=reason)
        if member.reason:
            await ctx.send(f'Unbanned {member.user} (ID: {member.user.id}), previously banned for {member.reason}.')
        else:
            await ctx.send(f'Unbanned {member.user} (ID: {member.user.id}).')


    @commands.group()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx):
        """Purges messages that meet a criteria.
        In order to use this command, you must have Manage Messages permissions.
        Note that the bot needs Manage Messages as well. These commands cannot
        be used in a private message.
        When the command is done doing its work, you will get a message
        detailing which users got purged and how many messages got purged.
        """

        if ctx.invoked_subcommand is None:
            help_cmd = self.bot.get_command('help')
            await ctx.invoke(help_cmd, command='purge')

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None):
        if limit > 2000:
            return await ctx.send(f'Too many messages to search given ({limit}/2000)')

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden as e:
            return await ctx.send('I do not have permissions to delete messages.')
        except discord.HTTPException as e:
            return await ctx.send(f'Error: {e} (try a smaller search?)')

        spammers = Counter(m.author.display_name for m in deleted)
        deleted = len(deleted)
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} purged.']
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'**{name}**: {count}' for name, count in spammers)

        to_send = '\n'.join(messages)

        if len(to_send) > 2000:
            await ctx.send(f'Successfully purged {deleted} messages.', delete_after=10)
        else:
            await ctx.send(to_send, delete_after=10)

    @purge.command()
    async def embeds(self, ctx, search=100):
        """Purges messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @purge.command()
    async def files(self, ctx, search=100):
        """purges messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @purge.command()
    async def images(self, ctx, search=100):
        """Purges messages that have embeds or attachments."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @purge.command(name='all')
    async def _purge_all(self, ctx, search=100):
        """Purges all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @purge.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Purges all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @purge.command()
    async def contains(self, ctx, *, substr: str):
        """Purges all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send('The substring length must be at least 3 characters.')
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @purge.command(name='bot')
    async def _bot(self, ctx, prefix=None, search=100):
        """Purges a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or (prefix and m.content.startswith(prefix))

        await self.do_removal(ctx, search, predicate)

    @purge.command(name='emoji')
    async def _emoji(self, ctx, search=100):
        """Purges all messages containing custom emoji."""
        custom_emoji = re.compile(r'<:(\w+):(\d+)>')
        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @purge.command(name='reactions')
    async def _reactions(self, ctx, search=100):
        """Purges all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(f'Too many messages to search for ({search}/2000)')

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f'Successfully purged {total_reactions} reactions.')

    @purge.command()
    async def custom(self, ctx, *, args: str):
        """A more advanced purge command.
        This command uses a powerful "command line" syntax.
        Most options support multiple values to indicate 'any' match.
        If the value has spaces it must be quoted.
        The messages are only deleted if all options are met unless
        the `--or` flag is passed, in which case only if any is met.
        The following options are valid.
        `--user`: A mention or name of the user to purge.
        `--contains`: A substring to search for in the message.
        `--starts`: A substring to search if the message starts with.
        `--ends`: A substring to search if the message ends with.
        `--search`: How many messages to search. Default 100. Max 2000.
        `--after`: Messages must come after this message ID.
        `--before`: Messages must come before this message ID.
        Flag options (no arguments):
        `--bot`: Check if it's a bot user.
        `--embeds`: Check if the message has embeds.
        `--files`: Check if the message has attachments.
        `--emoji`: Check if the message has custom emoji.
        `--reactions`: Check if the message has reactions
        `--or`: Use logical OR for all options.
        `--not`: Use logical NOT for all options.
        """
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--user', nargs='+')
        parser.add_argument('--contains', nargs='+')
        parser.add_argument('--starts', nargs='+')
        parser.add_argument('--ends', nargs='+')
        parser.add_argument('--or', action='store_true', dest='_or')
        parser.add_argument('--not', action='store_true', dest='_not')
        parser.add_argument('--emoji', action='store_true')
        parser.add_argument('--bot', action='store_const', const=lambda m: m.author.bot)
        parser.add_argument('--embeds', action='store_const', const=lambda m: len(m.embeds))
        parser.add_argument('--files', action='store_const', const=lambda m: len(m.attachments))
        parser.add_argument('--reactions', action='store_const', const=lambda m: len(m.reactions))
        parser.add_argument('--search', type=int, default=100)
        parser.add_argument('--after', type=int)
        parser.add_argument('--before', type=int)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await ctx.send(str(e))
            return

        predicates = []
        if args.bot:
            predicates.append(args.bot)

        if args.embeds:
            predicates.append(args.embeds)

        if args.files:
            predicates.append(args.files)

        if args.reactions:
            predicates.append(args.reactions)

        if args.emoji:
            custom_emoji = re.compile(r'<:(\w+):(\d+)>')
            predicates.append(lambda m: custom_emoji.search(m.content))

        if args.user:
            users = []
            converter = commands.MemberConverter()
            for u in args.user:
                try:
                    user = await converter.convert(ctx, u)
                    users.append(user)
                except Exception as e:
                    await ctx.send(str(e))
                    return

            predicates.append(lambda m: m.author in users)

        if args.contains:
            predicates.append(lambda m: any(sub in m.content for sub in args.contains))

        if args.starts:
            predicates.append(lambda m: any(m.content.startswith(s) for s in args.starts))

        if args.ends:
            predicates.append(lambda m: any(m.content.endswith(s) for s in args.ends))

        op = all if not args._or else any
        def predicate(m):
            r = op(p(m) for p in predicates)
            if args._not:
                return not r
            return r

        args.search = max(0, min(2000, args.search)) # clamp from 0-2000
        await self.do_removal(ctx, args.search, predicate, before=args.before, after=args.after)
    @commands.command(no_pm = True)
    @commands.has_permissions(manage_nicknames=True)
    async def setnickname(self, ctx, user : discord.Member = None, *, nick: str = None):

        """Changes the nickname of a user

        To use this command you must have the Managae Nicknames permissions.
        The bot must also have a Manage Roles permissions.

        This command cannot be used in a private message."""

        if user is None:
            await ctx.send(':exclamation: | {} you did not tell me whose nickname to change.'.format(ctx.message.author.mention))
            return

        if nick is None:
            await ctx.send(':exclamation: | {} you did not tell me what to change the {}\'s nickname.'.format(ctx.message.author.mention, user.name))

        try:
            await user.edit(nick=nick)
            await ctx.send(":ballot_box_with_check: | {} changed ``{}``\'s username.".format(ctx.message.author.mention, user.nick if user.nick else user.name))
        except discord.Forbidden:
            await ctx.send(':exclamation: | The bot does not have permissions to change nicknames.')
        except discord.HTTPException:
            await ctx.send(':exclamation: | Changing nickname failed.')
            
def setup(bot):
    m = Mod(bot)
    bot.add_cog(m)
