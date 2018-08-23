from discord.ext import commands
from itertools import cycle
# from cogs.utils import checks, config
import discord
import datetime, re
import json, asyncio
import copy
import logging
import sys
import ast
import asyncio
import asyncpg
import traceback
import aiohttp
from cogs.utils import context, db
from cogs.utils.config import Config
from collections import Counter, deque
import config
print ("[INFO] Discord version: " + discord.__version__)
description = """
Hello I am Putin. I hope to see you soon at Russia.
"""

initial_extensions = [
    'cogs.meta',
    'cogs.rng',
    'cogs.mod',
    'cogs.tags',
    'cogs.fun',
    'cogs.help2',
    'cogs.image',
    'cogs.profiles',
    'cogs.nekos',
    'cogs.prefix',
    'cogs.nsfw',
    'cogs.lyrics',
    'cogs.search',
    'cogs.dislogs',
    'cogs.link',
    'cogs.anime',
    'cogs.music',
    # 'cogs.custom',
    'cogs.stars',
    'cogs.rtfm',
    'cogs.poll',
    'cogs.chat',
    'cogs.osu',
    'cogs.emoji',
    'cogs.reminder',
    'cogs.stats',
    'cogs.admin'
]

log = logging.getLogger(__name__)

def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('.')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['.']))
        # base.append('.')
    return base

class Putin(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=_prefix_callable, description=description, fetch_offline_members=False)

        self.session = aiohttp.ClientSession(loop=self.loop)
        self._prev_events = deque(maxlen=10)
        self.add_command(self.do)
        self.remove_command('help')

        self.prefixes = Config('prefixes.json')

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f'failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

    def get_guild_prefixes(self, guild, *, local_inject=_prefix_callable):
        proxy_msg = discord.Object(id=None)
        proxy_msg.guild = guild
        return local_inject(self, proxy_msg)

    def get_raw_guild_prefixes(self, guild_id):
        return self.prefixes.get(guild_id, ['.'])

    async def set_guild_prefixes(self, guild, prefixes):
        if len(prefixes) == 0:
            await self.prefixes.put(guild.id, [])
        elif len(prefixes) > 10:
            raise RuntimeError('Cannot have more than 10 custom prefixes.')
        else:
            await self.prefixes.put(guild.id, sorted(set(prefixes), reverse=True))

# bot = commands.Bot(command_prefix=get_pre, description=description)
# bot.remove_command('help')
    

    @property
    def config(self):
        return __import__('config')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shell(self, ctx, *, _code: str):
        async def run_cmd(self, cmd: str) -> str:
            """Runs a subprocess and returns the output."""
            process =\
                await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            results = await process.communicate()
            return "".join(x.decode("utf-8") for x in results)
        print(_code)
        console = await run_cmd(self, _code)
        print(console)
        await ctx.send('```shell\n{}```'.format(console))

    async def on_guild_join(self, guild):
        print("Joined guild: {}.".format(guild.name))
        await guild.owner.send("```Hey nice to see that you invited me!\nIf you need any help use \".help\" anywhere on the guild.\nJoin the bot\'s support guildat here: https://discord.gg/GJvq24V.```")
        general=self.get_channel(478265028185948162)
        await general.send('I just joined a new guild called ``{}``.'.format(guild.name))

    async def on_member_join(self, member):
        guild = member.guild
        if guild.id == 329993146651901952:
                role = discord.utils.get(member.guild.roles, name='Member')
                try:
                    await member.add_roles(role)
                except discord.Forbidden:
                    member.guild.send('I do not have proper permissions or high enough rank to give roles.')
        else:
            return

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(ctx.message.author, 'This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(ctx.message.author, 'Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.BadArgument):
            await ctx.send(error)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('You do not have **{}** permissions. You need them to use this command.'.format(error.missing_perms[0]))
        elif isinstance(error, commands.NotOwner):
            await ctx.send('Only my creator can use this command.')



    async def on_ready(self):
        print('[INFO] Bot is online')
        print('[NAME] ' + self.user.name)
        print('[ ID ] ' + str(self.user.id))
        print('[]---------------------------[]')
        # general = bot.get_channel(337968532388184066)
        # await general.send("Ayy, feels good to be back :relaxed:")
        self.uptime = datetime.datetime.utcnow()
        self.commands_executed = 0
        async def send_files():
            while True:
                files = [discord.File('profiles.json'), discord.File('tags.json'), discord.File('prefixes.json'), discord.File('logs.json'), discord.File('rooms.json'), discord.File('mod.json'), discord.File('commands.json')]
                channel = self.get_channel(478363328448823317)
                await channel.send(files=files)
                await asyncio.sleep(300)
        # await send_files()
        self.load_extension('cogs.dbl')

    async def on_command(self, ctx):
        self.commands_executed += 1
        message = ctx.message
        destination = '#{0.channel.name} ({0.guild.name})'.format(message)
        if isinstance(message.channel, discord.DMChannel):
            destination = '{}\'s dmchannel'
        logger = logging.getLogger('__main__')
        logger.info('{0.created_at}: {0.author.name} in {1}: {0.content}'.format(message, destination))

    async def on_message(self, message):
        if not message.author.bot:
            mod = self.get_cog('Mod')

            if mod is not None and not message.author.id == 282515230595219456:
                perms = message.channel.permissions_for(message.author)
                bypass_ignore = perms.manage_roles

                if not bypass_ignore:
                    if message.channel.id in mod.config.get('ignored', []):
                        return
            await self.process_commands(message)

    @commands.command(hidden=True)
    async def shutdown(self, ctx):
        await ctx.send(':wave: Cya!')
        await self.logout()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def do(self, ctx, times: int, *, command):
        """Repeats a command a specified number of times."""
        msg = copy.copy(ctx.message)
        msg.content = command

        new_ctx = await self.get_context(msg, cls=context.Context)
        new_ctx.db = ctx.db

    async def on_resumed(self):
        print('resumed...')

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=context.Context)

        if ctx.command is None:
            return

        # async with ctx.acquire():
        await self.invoke(ctx)

    async def close(self):
        await super().close()
        await self.session.close()

    def run(self):
        try:
            super().run(config.token, reconnect=True)
        finally:
            with open('prev_events.log', 'w', encoding='utf-8') as fp:
                for data in self._prev_events:
                    try:
                        x = json.dumps(data, ensure_ascii=True, indent=4)
                    except:
                        fp.write(f'{data}\n')
                    else:
                        fp.write(f'{x}\n')

# if __name__ == '__main__':
#     bot.run('NDYwODQ2MjkxMzAwMTIyNjM1.DlIJQw.HZ8z8bJRaaTdfJ_DVayZi6_SCQw')
#     # bot.run('NDYyMDIwMTUxODY5NTcxMDky.DjnaLw.MADh6nQZwdC8QLTWZNR4bc4G9A0')
#     handlers = logger.handlers[:]
#     for hdlr in handlers:
#         hdlr.close()
#         logger.removeHandler(hdlr)
