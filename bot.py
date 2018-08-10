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
    'cogs.dbl',
    'cogs.lyrics',
    'cogs.search',
    'cogs.dislogs',
    'cogs.link',
    'cogs.anime',
    'cogs.music',
    'cogs.custom',
    'cogs.chat',
    'cogs.osu'
]

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.CRITICAL)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='putin.log', encoding='utf-8', mode='w')
logger.addHandler(handler)

async def get_pre(bot, message):
    prefixes = []
    with open('prefixes.json') as file:
        data = json.load(file)
    if str(message.guild.id) in data:
        prefix = data[str(message.guild.id)]
    else:
        prefix = None

    if prefix is not None:
        prefixes.append(prefix)
    prefixes.append('.')
    prefixes.append('<@460846291300122635> ')
    return prefixes

# help_attrs = dict(hidden=True)
status = ['Hello there.', 'Cya at Russia.']
bot = commands.Bot(command_prefix=get_pre, description=description)
bot.remove_command('help')

async def change_status():
    await bot.wait_until_ready()
    msgs = cycle(status)

    while not bot.is_closed:
        current_status = next(msgs)
        game = discord.Game(current_status)
        await bot.change_presence(status=discord.Status.online, activity=game)
        await asyncio.sleep(5)

async def run_cmd(cmd: str) -> str:
    """Runs a subprocess and returns the output."""
    process =\
        await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    results = await process.communicate()
    return "".join(x.decode("utf-8") for x in results)

@bot.command(hidden=True)
@commands.is_owner()
async def shell(ctx, code: str):
    console = await run_cmd(code)
    await ctx.send('```shell\n{}```'.format(console))

@bot.command(hidden=True)
@commands.is_owner()
async def presence(self, ctx, *, text: str=None):
    game = discord.Game(text)
    await bot.change_presence(activity=game)

@bot.event
async def on_guild_join(guild):
    print("Joined guild: {}.".format(guild.name))
    await guild.owner.send("```Hey nice to see that you invited me!\nIf you need any help use \".help\" anywhere on the guild.\nJoin the bot\'s support guildat here: https://discord.gg/GJvq24V.```")
    general=bot.get_channel(337968532388184066)
    await general.send('The bot just joined a new guild called ``{}``.'.format(guild.name))

@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.id == 329993146651901952:
            role = discord.utils.get(member.guild.roles, name='Member')
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                member.guild.send('I do not have proper permissions or high enough rank to give roles.')
    else:
        return

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send(ctx.message.author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send(ctx.message.author, 'Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Something went wrong with the arguments you passed in.\nAn argument can be e.g. a member/user or a channel etc. Please note that this is case-sensitive.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('You do not have **{}** permissions. You need them to use this command.'.format(error.missing_perms[0]))
    elif isinstance(error, commands.NotOwner):
        await ctx.send('Only my creator can use this command.')

@bot.event
async def on_ready():
    print('[INFO] Bot is online')
    print('[NAME] ' + bot.user.name)
    print('[ ID ] ' + str(bot.user.id))
    print('[]---------------------------[]')
    general = bot.get_channel(337968532388184066)
    await general.send("Ayy, feels good to be back :relaxed:")
    bot.uptime = datetime.datetime.utcnow()
    bot.commands_executed = 0

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

@bot.event
async def on_command(ctx):
    bot.commands_executed += 1
    message = ctx.message
    destination = '#{0.channel.name} ({0.guild.name})'.format(message)

    logger.info('{0.created_at}: {0.author.name} in {1}: {0.content}'.format(message, destination))

@bot.event
async def on_message(message):
    if not message.author.bot:
        mod = bot.get_cog('Mod')

        if mod is not None and not message.author.id == 282515230595219456:
            perms = message.channel.permissions_for(message.author)
            bypass_ignore = perms.manage_roles

            if not bypass_ignore:
                if message.channel.id in mod.config.get('ignored', []):
                    return
        await bot.process_commands(message)

@bot.command(hidden=True)
async def shutdown(ctx):
    await ctx.send(':wave: Cya!')
    await bot.logout()

@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, *, module : str):
    """Loads a module."""
    module = module.strip()
    if 'cogs.' not in module:
        module = 'cogs.' +  module
    try:
        bot.load_extension(module)
    except Exception as e:
        await ctx.send('\U0001f52b')
        await ctx.send('{}: {}'.format(type(e).__name__, e))
    else:
        await ctx.send('\U0001f44c')

@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, *, module : str):
    """Unloads a module."""
    module = module.strip()
    if 'cogs.' not in module:
        module = 'cogs.' +  module
    try:
        bot.unload_extension(module)
    except Exception as e:
        await ctx.send('\U0001f52b')
        await ctx.send('{}: {}'.format(type(e).__name__, e))
    else:
        await ctx.send('\U0001f44c')

@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, *, module : str):
    module = module.strip()
    if 'cogs.' not in module:
        module = 'cogs.' +  module
    try:
        bot.unload_extension(module)
        bot.load_extension(module)
    except Exception as e:
        await ctx.send('\U0001f52b')
        await ctx.send('{}: {}'.format(type(e).__name__, e))
    else:
        await ctx.send('\U0001f44c')

@bot.command(hidden=True)
@commands.is_owner()
async def ev(ctx, *, code : str):
    if not ctx.message.author.id  == 282515230595219456: return
    """Evaluates code."""
    code = code.strip('` ')
    python = '```py\n{}\n```'
    result = None

    try:
        result = eval(code)
    except Exception as e:
        await ctx.send(python.format(type(e).__name__ + ': ' + str(e)))
        return

    if asyncio.iscoroutine(result):
        result = await result

    await ctx.send(python.format(result))

@bot.command(hidden=True)
@commands.is_owner()
async def guilds(ctx):
    guilds = list(bot.guilds)
    await ctx.send("Connected to " + str(len(bot.guilds)) + " guilds:")
    print("Connected to " + str(len(bot.guilds)) + " guilds:")
    for x in range(len(guilds)):
        await ctx.send(" {}".format(guilds[x-1].name))
        print(" {}".format(guilds[x-1].name))

# @bot.command(hidden=True)
# @commands.is_owner()
# async def announcement(ctx, *, message : str):
#     # we copy the list over so it doesn't change while we're iterating over it
#     guilds = list(bot.guilds)
#     for guild in guilds:
#         try:
#             await ctx.send(guild, message)
#         except discord.Forbidden:
#             # we can't send a message for some reason in this
#             # channel, so try to look for another one.
#             me = guild.me
#             def predicate(ch):
#                 text = ch.type == discord.ChannelType.text
#                 return text and ch.permissions_for(me).send_messages

#             channel = discord.utils.find(predicate, guild.channels)
#             if channel is not None:
#                 await ctx.send(channel, message)
#         finally:
#             print('Sent message to {}'.format(guild.name.encode('utf-8')))
#             # to make sure we don't hit the rate limit, we send one
#             # announcement message every 5 seconds.
#             await asyncio.sleep(5)

@bot.command(hidden=True)
@commands.is_owner()
async def do(ctx, times : int, *, command):
    """Repeats a command a specified number of times."""
    msg = copy.copy(ctx.message)
    msg.content = command
    for i in range(times):
        await bot.process_commands(msg)

if __name__ == '__main__':
    bot.loop.create_task(change_status())
    bot.run('NDYwODQ2MjkxMzAwMTIyNjM1.Djnshw.d1T4A4GsvirNk1Lt2QH09givOns')
    # bot.run('NDYyMDIwMTUxODY5NTcxMDky.DjnaLw.MADh6nQZwdC8QLTWZNR4bc4G9A0')
    handlers = logger.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        logger.removeHandler(hdlr)
