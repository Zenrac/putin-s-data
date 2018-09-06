"""Discord bot made by iWeeti"""
import datetime
import json
import copy
import logging
import sys
import traceback
from collections import deque
import aiohttp
import discord

from discord.ext import commands
from discord.utils import get

from cogs.utils import context
from cogs.utils.config import Config

import config

print("[INFO] Discord version: " + discord.__version__)

DESCRIPTION = """
Hello I am Putin. I hope to see you soon at Russia.
"""

INITIAL_EXTENSIONS = [
    'cogs.meta',
    'cogs.rng',
    'cogs.mod',
    'cogs.tags',
    'cogs.fun',
    'cogs.help',
    'cogs.image',
    'cogs.profiles',
    'cogs.nekos',
    'cogs.nsfw',
    'cogs.search',
    'cogs.dislogs',
    'cogs.link',
    'cogs.music',
    'cogs.stars',
    'cogs.rtfm',
    'cogs.poll',
    'cogs.emoji',
    'cogs.reminder',
    'cogs.stats',
    'cogs.admin',
    'cogs.settings',
    'cogs.dbl',
    'cogs.config'
]

def _prefix_callable(bot, msg):
    """Gets the prefix for a command."""
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('.')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['.']))
        # base.append('.')
    return base

class Putin(commands.AutoShardedBot):
    """Discord bot made by iWeeti#4990."""
    def __init__(self):
        super().__init__(command_prefix=_prefix_callable,
                         description=DESCRIPTION,
                         fetch_offline_members=False)

        self.session = aiohttp.ClientSession(loop=self.loop)
        self.commands_executed = 0
        self._prev_events = deque(maxlen=10)
        self.add_command(self._do)
        self.add_command(self.setup)
        self.remove_command('help')
        self.uptime = datetime.datetime.utcnow()

        self.prefixes = Config('prefixes.json')

        for extension in INITIAL_EXTENSIONS:
            try:
                self.load_extension(extension)
                print(f'[INFO] {extension} loaded.')
            except ModuleNotFoundError:
                print(f'[FAIL] Extension {extension} not found.', file=sys.stderr)
            except:
                print(f'[FAIL] Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

    logger = logging.getLogger('__main__')

    @property
    def config(self):
        """Returns the config."""
        return __import__('config')

    def get_guild_prefixes(self, guild, *, local_inject=_prefix_callable):
        """Gets the guild prefixes."""
        proxy_msg = discord.Object(id=None)
        proxy_msg.guild = guild
        return local_inject(self, proxy_msg)

    def get_raw_guild_prefixes(self, guild_id):
        """Gets the raw guild prefixes."""
        return self.prefixes.get(guild_id, ['.'])

    async def set_guild_prefixes(self, guild, prefixes):
        """Sets the guild prefixes."""
        if not prefixes[0]:
            await self.prefixes.put(guild.id, [])
        elif len(prefixes) > 10:
            raise RuntimeError('Cannot have more than 10 custom prefixes.')
        else:
            await self.prefixes.put(guild.id, sorted(set(prefixes), reverse=True))

    async def on_guild_join(self, guild):
        """This triggers when the bot joins a guild."""
        game = discord.Activity(name=f"slaves in {len(self.guilds)} servers.",
                                type=discord.ActivityType.watching)
        await self.change_presence(status=discord.Status.online, activity=game)
        if guild.id == 421630709585805312:
            return
        try:
            channel = await guild.create_text_channel('putin-logging')
            overwrite = discord.PermissionOverwrite(read_messages=False)
            role = guild.default_role
            await channel.set_permissions(role, overwrite=overwrite)
            await guild.owner.send(f'Hey, it seems that you own **{guild.name}**'
                                   ' and I have been invited to there.'\
                                   'Run ``.settings`` to get started.')
            await channel.send('To get started run ``.settings``.'\
                               'If you need more info join here https://discord.gg/Ry4JQRf.' \
                               'You can also check my commands by running ``.help``.')
        except discord.Forbidden:
            await guild.owner.send('Please let me have Create channels'
                                   ' permissions so you can get started.'\
                                   'After you have setted up the permissions, run ``.setup``.')

    async def on_member_join(self, member):
        """This triggers when someone joins a guild the bot is in."""
        guild = member.guild
        if guild.id == 329993146651901952:
            role = discord.utils.get(member.guild.roles, name='Member')
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                member.guild.send('I do not have proper permissions'
                                  ' or high enough rank to give roles.')
        else:
            return

    async def on_command_error(self, ctx, error):
        """This triggers when an error occurs in a command."""
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(ctx.message.author, 'This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(ctx.message.author, 'Sorry. This command is disabled'
                                               ' and cannot be used.')
        elif isinstance(error, commands.BadArgument):
            await ctx.send(error.replace('int', 'number'))
        elif isinstance(error, commands.MissingPermissions):
            missing_perms = error.missing_perms[0].replace('_', ' ')
            await ctx.send(f'You do not have **{missing_perms}** permissions.'
                           ' You need them to use this command.')
        elif isinstance(error, commands.BotMissingPermissions):
            missing_perms = ", ".join(_perms.replace('_', ' ') for _perms in error.missing_perms)
            await ctx.send(f'You do not have **{missing_perms}** permissions.'
                           ' You need them to use this command.')
        elif isinstance(error, commands.NotOwner):
            await ctx.send('Only my creator can use this command.')
        if isinstance(error, commands.CommandOnCooldown):
            minutes, s = divmod(error.retry_after, 60)
            hours, minutes = divmod(m, 60)
            if hours > 1:
                hours = f'{hours} hours'
            elif hours == 0:
                hours = ''
            else:
                hours = f'{hours} hour'
            if minutes > 2:
                minutes = f'{minutes} minutes'
            elif minutes == 0:
                minutes = ''
            else:
                minutes = f'{minutes} minute'
            if seconds > 2:
                seconds = f'{seconds} seconds'
            elif seconds == 0:
                seconds = ''
            else:
                seconds = f'{seconds} second'
            await ctx.send(f'This command is on cooldown for {hours} {minutes} {seconds}.')

    async def on_ready(self):
        """This triggers when the bot is ready."""
        print('[INFO] Bot is online')
        print('[NAME] ' + self.user.name)
        print('[ ID ] ' + str(self.user.id))
        print('[]---------------------------[]')
        self.commands_executed = 0
        game = discord.Activity(name=f"slaves in {len(self.guilds)} servers.", type=discord.ActivityType.watching)
        await self.change_presence(status=discord.Status.online, activity=game)

    async def on_command(self, ctx):
        """This triggers when a command is invoked."""
        self.commands_executed += 1
        message = ctx.message
        destination = '#{0.channel.name} ({0.guild.name})'.format(message)
        if isinstance(message.channel, discord.DMChannel):
            destination = '{}\'s dmchannel'
        logger = logging.getLogger('__main__')
        logger.info('{0.created_at}: {0.author.name} in {1}:'
                    ' {0.content}'.format(message, destination))

    async def on_message(self, message):
        """This triggers when the bot can see a message being sent."""
        if not message.author.bot:
            # mod = self.get_cog('Mod')

            # if mod is not None and not message.author.id == 282515230595219456:
            #     perms = message.channel.permissions_for(message.author)
            #     bypass_ignore = perms.manage_roles

            #     if not bypass_ignore:
            #         if message.channel.id in mod.config.get('ignored', []):
            #             return
            await self.process_commands(message)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        """Sets up the logging channel."""
        already = get(ctx.guild.channels, name='putin-logging')
        if already:
            return await ctx.send('Seems that you already have a'
                                  ' channel called ``putin-logging`` please'
                                  ' delete it to set me up.')
        channel = await ctx.guild.create_text_channel('putin-logging')
        overwrite = discord.PermissionOverwrite(read_messages=False)
        role = ctx.guild.default_role
        await channel.set_permissions(role, overwrite=overwrite)
        await ctx.bot.pool.execute(f'insert into settings values({ctx.guild.id}, true)')
        await channel.send('Alright to get started use ``.settings``.'\
                           'If you want to see my commands use ``.help``.')

    @commands.command(hidden=True)
    async def shutdown(self, ctx):
        """Shuts down the bot."""
        await ctx.send(':wave: Cya!')
        await self.logout()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def _do(self, ctx, times: int, *, command):
        """Repeats a command a specified number of times."""
        msg = copy.copy(ctx.message)
        msg.content = command

        new_ctx = await self.get_context(msg, cls=context.Context)
        new_ctx.db = ctx.db

        for i in range(times):
            i = i
            await new_ctx.reinvoke()

    async def on_resumed(self):
        """This triggers when the bot resumed after an outage."""
        print('[INFO] Resumed...')

    async def process_commands(self, message):
        """This processes the commands."""
        ctx = await self.get_context(message, cls=context.Context)

        if ctx.command is None:
            return

        async with ctx.acquire():
            await self.invoke(ctx)

    async def close(self):
        await super().close()
        await self.session.close()

    def run(self):
        try:
            super().run(config.token, reconnect=True)
        finally:
            with open('prev_events.log', 'w', encoding='utf-8') as _fp:
                for data in self._prev_events:
                    try:
                        _x = json.dumps(data, ensure_ascii=True, indent=4)
                    except:
                        _fp.write(f'{data}\n')
                    else:
                        _fp.write(f'{_x}\n')
